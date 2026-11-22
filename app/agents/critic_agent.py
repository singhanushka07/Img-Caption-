import io
import base64
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from openai import OpenAI

from app.config import settings

_JUDGE_PROMPT = """\
Evaluate the following caption for this image.

Caption: "{caption}"
Style requested: {style}

Rate the caption on a scale of 1-10 for each criterion:
1. Accuracy: How well does it describe what's in the image?
2. Detail: Is the level of detail appropriate for the style?
3. Style Match: Does it match the requested '{style}' style?
4. Fluency: Is it well-written and natural?

Respond ONLY in this exact format (one value per line):
accuracy: <number>
detail: <number>
style_match: <number>
fluency: <number>
overall: <number>
reason: <one sentence explanation>"""


class CriticAgent:
    _clip_model = None
    _clip_processor = None

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.has_openai else None
        self._load_clip()

    @classmethod
    def _load_clip(cls):
        if cls._clip_model is None:
            try:
                cls._clip_processor = CLIPProcessor.from_pretrained(settings.clip_model_name)
                cls._clip_model = CLIPModel.from_pretrained(settings.clip_model_name)
                cls._clip_model.eval()
            except Exception:
                pass

    # ── CLIPScore ─────────────────────────────────────────────────────────────

    def compute_clip_score(self, image: Image.Image, caption: str) -> float:
        if self._clip_model is None or self._clip_processor is None:
            self._load_clip()
        if self._clip_model is None or self._clip_processor is None:
            return 0.0
        try:
            image_rgb = image.convert("RGB")
            inputs = self._clip_processor(
                text=[caption], images=image_rgb, return_tensors="pt", padding=True
            )
            with torch.no_grad():
                outputs = self._clip_model(**inputs)
            ie = outputs.image_embeds
            te = outputs.text_embeds
            ie = ie / ie.norm(dim=-1, keepdim=True)
            te = te / te.norm(dim=-1, keepdim=True)
            return float(torch.nn.functional.cosine_similarity(ie, te).item())
        except Exception:
            return 0.0

    # ── LLM judge ─────────────────────────────────────────────────────────────

    def llm_judge_evaluate(self, image: Image.Image, caption: str, style: str) -> dict:
        image_rgb = image.convert("RGB")
        buf = io.BytesIO()
        image_rgb.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        prompt = _JUDGE_PROMPT.format(caption=caption, style=style)

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}",
                                "detail": "low",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=200,
            temperature=0.1,
            timeout=20.0,
        )
        return self._parse_judge_response(response.choices[0].message.content)

    def _parse_judge_response(self, text: str) -> dict:
        defaults = {
            "accuracy": 5,
            "detail": 5,
            "style_match": 5,
            "fluency": 5,
            "overall": 5,
            "reason": "",
        }
        for line in text.strip().splitlines():
            line = line.strip()
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().lower().replace(" ", "_")
            value = value.strip()
            if key not in defaults:
                continue
            if key == "reason":
                defaults["reason"] = value
            else:
                try:
                    defaults[key] = max(1, min(10, int(float(value))))
                except ValueError:
                    pass
        return defaults

    # ── Main evaluate ─────────────────────────────────────────────────────────

    def evaluate(self, image: Image.Image, caption: str, style: str) -> dict:
        clip_score = self.compute_clip_score(image, caption)
        passes_clip = clip_score >= settings.clip_score_threshold

        if not settings.has_openai:
            # Offline mode: accept if CLIPScore passes
            return {
                "clip_score": clip_score,
                "judge_scores": {
                    "accuracy": 7, "detail": 7, "style_match": 7, "fluency": 7,
                    "overall": 7,
                    "reason": "LLM judge skipped — no OpenAI API key configured.",
                },
                "passes_clip": passes_clip,
                "passes_judge": True,
                "passes": passes_clip,
            }

        try:
            judge_scores = self.llm_judge_evaluate(image, caption, style)
        except Exception as exc:
            judge_scores = {
                "accuracy": 5, "detail": 5, "style_match": 5, "fluency": 5,
                "overall": 5,
                "reason": f"Judge evaluation failed: {exc}",
            }

        passes_judge = judge_scores["overall"] >= settings.llm_judge_threshold

        # If CLIP model isn't downloaded yet or failed, rely on the LLM judge
        clip_available = self._clip_model is not None and clip_score > 0.0
        passes_clip_effective = passes_clip if clip_available else True
        passes = passes_clip_effective and passes_judge

        return {
            "clip_score": clip_score,
            "judge_scores": judge_scores,
            "passes_clip": passes_clip,
            "passes_judge": passes_judge,
            "passes": passes,
        }
