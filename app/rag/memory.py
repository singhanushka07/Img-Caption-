import os
import json
import hashlib
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass, asdict
from PIL import Image

from app.config import settings


CLIP_DIM = 512


@dataclass
class CaptionEntry:
    image_hash: str
    caption: str
    style: str
    model_name: str
    clip_score: float = 0.0
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RAGMemory:
    _clip_model = None
    _clip_processor = None

    def __init__(self):
        self.encoder = SentenceTransformer(settings.sentence_transformer_model)
        self.dimension = self.encoder.get_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.image_index = faiss.IndexFlatIP(CLIP_DIM)
        self.entries: list[CaptionEntry] = []
        self._load()

    @classmethod
    def _load_clip(cls):
        if cls._clip_model is None:
            try:
                from transformers import CLIPProcessor, CLIPModel
                cls._clip_processor = CLIPProcessor.from_pretrained(settings.clip_model_name)
                cls._clip_model = CLIPModel.from_pretrained(settings.clip_model_name)
                cls._clip_model.eval()
            except Exception:
                pass

    def _get_image_embedding(self, image: Image.Image) -> np.ndarray | None:
        self._load_clip()
        if self._clip_model is None or self._clip_processor is None:
            return None
        try:
            image_rgb = image.convert("RGB")
            inputs = self._clip_processor(images=image_rgb, return_tensors="pt")
            with torch.no_grad():
                emb = self._clip_model.get_image_features(**inputs)
            emb = emb / emb.norm(dim=-1, keepdim=True)
            return emb.cpu().numpy().astype(np.float32)
        except Exception:
            return None

    def add_caption(
        self,
        image_hash: str,
        caption: str,
        style: str,
        model_name: str,
        clip_score: float = 0.0,
        metadata: dict = None,
        image: Image.Image = None,
    ):
        entry = CaptionEntry(
            image_hash=image_hash,
            caption=caption,
            style=style,
            model_name=model_name,
            clip_score=clip_score,
            metadata=metadata or {},
        )
        embedding = self.encoder.encode([caption], normalize_embeddings=True)
        self.index.add(np.array(embedding, dtype=np.float32))

        if image is not None:
            img_emb = self._get_image_embedding(image)
            if img_emb is not None:
                self.image_index.add(img_emb)
            else:
                self.image_index.add(np.zeros((1, CLIP_DIM), dtype=np.float32))
        else:
            self.image_index.add(np.zeros((1, CLIP_DIM), dtype=np.float32))

        self.entries.append(entry)
        self._save()

    def retrieve_similar(self, query_text: str, k: int = 3) -> list[CaptionEntry]:
        if self.index.ntotal == 0:
            return []

        k = min(k, self.index.ntotal)
        query_embedding = self.encoder.encode(
            [query_text], normalize_embeddings=True
        )
        scores, indices = self.index.search(
            np.array(query_embedding, dtype=np.float32), k
        )

        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.entries):
                results.append(self.entries[idx])
        return results

    def retrieve_by_image(self, image: Image.Image, k: int = 3) -> list[tuple[CaptionEntry, float]]:
        if self.image_index.ntotal == 0:
            return []

        img_emb = self._get_image_embedding(image)
        if img_emb is None:
            return []

        k = min(k, self.image_index.ntotal)
        scores, indices = self.image_index.search(img_emb, k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.entries):
                results.append((self.entries[idx], float(scores[0][i])))
        return results

    def retrieve_combined(
        self, query_text: str, image: Image.Image = None, k: int = 3,
    ) -> list[CaptionEntry]:
        if self.index.ntotal == 0:
            return []

        n = self.index.ntotal
        fetch_k = min(n, max(k * 2, 10))

        text_emb = self.encoder.encode([query_text], normalize_embeddings=True)
        text_scores, text_indices = self.index.search(
            np.array(text_emb, dtype=np.float32), fetch_k,
        )

        text_weight = 1.0 - settings.clip_image_weight
        image_weight = settings.clip_image_weight

        img_emb = None
        img_scores_map = {}
        if image is not None and self.image_index.ntotal > 0:
            img_emb = self._get_image_embedding(image)
            if img_emb is not None:
                img_scores, img_indices = self.image_index.search(img_emb, fetch_k)
                for i, idx in enumerate(img_indices[0]):
                    if idx >= 0:
                        img_scores_map[int(idx)] = float(img_scores[0][i])

        scored = []
        for i, idx in enumerate(text_indices[0]):
            if idx < 0 or idx >= len(self.entries):
                continue
            t_score = float(text_scores[0][i])
            i_score = img_scores_map.get(int(idx), 0.0)
            if img_emb is not None:
                combined = text_weight * t_score + image_weight * i_score
            else:
                combined = t_score
            scored.append((combined, self.entries[idx]))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:k]]

    def get_context_string(
        self, query: str, style: str = None, k: int = 3,
        image: Image.Image = None,
    ) -> str:
        if image is not None:
            similar = self.retrieve_combined(query, image=image, k=k)
        else:
            similar = self.retrieve_similar(query, k=k)

        if not similar:
            return ""

        if style:
            styled = [e for e in similar if e.style == style]
            if styled:
                similar = styled

        lines = ["Here are some reference captions for similar images:"]
        for i, entry in enumerate(similar, 1):
            lines.append(f"{i}. [{entry.style}] {entry.caption}")
        return "\n".join(lines)

    @staticmethod
    def compute_image_hash(image_bytes: bytes) -> str:
        return hashlib.md5(image_bytes).hexdigest()

    def _save(self):
        os.makedirs(settings.faiss_index_path, exist_ok=True)
        index_path = os.path.join(settings.faiss_index_path, "caption_index.faiss")
        entries_path = os.path.join(settings.faiss_index_path, "entries.json")
        image_index_path = os.path.join(settings.faiss_index_path, "clip_image_index.faiss")

        faiss.write_index(self.index, index_path)
        faiss.write_index(self.image_index, image_index_path)
        with open(entries_path, "w") as f:
            json.dump([asdict(e) for e in self.entries], f, indent=2)

    def _load(self):
        index_path = os.path.join(settings.faiss_index_path, "caption_index.faiss")
        entries_path = os.path.join(settings.faiss_index_path, "entries.json")
        image_index_path = os.path.join(settings.faiss_index_path, "clip_image_index.faiss")

        if os.path.exists(index_path) and os.path.exists(entries_path):
            self.index = faiss.read_index(index_path)
            with open(entries_path) as f:
                data = json.load(f)
                self.entries = [CaptionEntry(**e) for e in data]

        if os.path.exists(image_index_path):
            self.image_index = faiss.read_index(image_index_path)
