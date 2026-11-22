import pytest
import tempfile
import os
import numpy as np
from unittest.mock import patch, MagicMock
from PIL import Image

from app.rag.memory import RAGMemory, CaptionEntry, CLIP_DIM


class TestRAGMemory:
    @patch("app.rag.memory.settings")
    def test_add_and_retrieve(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.sentence_transformer_model = "all-MiniLM-L6-v2"
            mock_settings.faiss_index_path = tmpdir

            memory = RAGMemory()

            memory.add_caption(
                image_hash="abc123",
                caption="A beautiful sunset over the ocean with orange and pink clouds",
                style="descriptive",
                model_name="BLIP",
                clip_score=0.3,
            )

            memory.add_caption(
                image_hash="def456",
                caption="A cat sitting on a windowsill",
                style="concise",
                model_name="gpt-4o-mini",
                clip_score=0.35,
            )

            results = memory.retrieve_similar("sunset over water", k=2)
            assert len(results) == 2
            assert any("sunset" in r.caption.lower() for r in results)

    @patch("app.rag.memory.settings")
    def test_empty_retrieval(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.sentence_transformer_model = "all-MiniLM-L6-v2"
            mock_settings.faiss_index_path = tmpdir

            memory = RAGMemory()
            results = memory.retrieve_similar("anything", k=3)
            assert results == []

    def test_caption_entry_defaults(self):
        entry = CaptionEntry(
            image_hash="test",
            caption="test caption",
            style="descriptive",
            model_name="BLIP",
        )
        assert entry.clip_score == 0.0
        assert entry.metadata == {}

    @patch("app.rag.memory.settings")
    def test_context_string_generation(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.sentence_transformer_model = "all-MiniLM-L6-v2"
            mock_settings.faiss_index_path = tmpdir

            memory = RAGMemory()
            memory.add_caption(
                image_hash="abc",
                caption="A dog playing in the park",
                style="descriptive",
                model_name="BLIP",
            )

            context = memory.get_context_string("dog at park", style="descriptive")
            assert "reference captions" in context.lower()
            assert "dog" in context.lower()

    @patch("app.rag.memory.settings")
    def test_compute_image_hash(self, mock_settings):
        hash1 = RAGMemory.compute_image_hash(b"image data 1")
        hash2 = RAGMemory.compute_image_hash(b"image data 2")
        hash3 = RAGMemory.compute_image_hash(b"image data 1")
        assert hash1 != hash2
        assert hash1 == hash3

    @patch("app.rag.memory.settings")
    def test_add_caption_with_image(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.sentence_transformer_model = "all-MiniLM-L6-v2"
            mock_settings.faiss_index_path = tmpdir
            mock_settings.clip_model_name = "openai/clip-vit-base-patch32"

            memory = RAGMemory()

            fake_emb = np.random.randn(1, CLIP_DIM).astype(np.float32)
            fake_emb = fake_emb / np.linalg.norm(fake_emb)

            with patch.object(memory, "_get_image_embedding", return_value=fake_emb):
                test_image = Image.new("RGB", (224, 224), color=(128, 128, 128))
                memory.add_caption(
                    image_hash="img001",
                    caption="A gray test image",
                    style="descriptive",
                    model_name="BLIP",
                    clip_score=0.3,
                    image=test_image,
                )

            assert memory.index.ntotal == 1
            assert memory.image_index.ntotal == 1
            assert len(memory.entries) == 1

    @patch("app.rag.memory.settings")
    def test_retrieve_combined(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.sentence_transformer_model = "all-MiniLM-L6-v2"
            mock_settings.faiss_index_path = tmpdir
            mock_settings.clip_model_name = "openai/clip-vit-base-patch32"
            mock_settings.clip_image_weight = 0.4

            memory = RAGMemory()

            fake_emb = np.random.randn(1, CLIP_DIM).astype(np.float32)
            fake_emb = fake_emb / np.linalg.norm(fake_emb)

            with patch.object(memory, "_get_image_embedding", return_value=fake_emb):
                test_image = Image.new("RGB", (224, 224), color=(128, 128, 128))
                memory.add_caption(
                    image_hash="img001",
                    caption="A dog in the park",
                    style="descriptive",
                    model_name="BLIP",
                    image=test_image,
                )
                memory.add_caption(
                    image_hash="img002",
                    caption="A sunset over the ocean",
                    style="descriptive",
                    model_name="BLIP",
                    image=test_image,
                )

                results = memory.retrieve_combined(
                    "dog playing outside", image=test_image, k=2
                )

            assert len(results) == 2
            assert all(isinstance(r, CaptionEntry) for r in results)

    @patch("app.rag.memory.settings")
    def test_backward_compat_no_image_index(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.sentence_transformer_model = "all-MiniLM-L6-v2"
            mock_settings.faiss_index_path = tmpdir

            memory = RAGMemory()
            memory.add_caption(
                image_hash="abc",
                caption="test caption",
                style="descriptive",
                model_name="BLIP",
            )
            memory._save()

            image_index_path = os.path.join(tmpdir, "clip_image_index.faiss")
            if os.path.exists(image_index_path):
                os.remove(image_index_path)

            memory2 = RAGMemory()
            assert len(memory2.entries) == 1
            assert memory2.image_index.ntotal == 0
