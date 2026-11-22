import time
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

from app.config import settings
from app.models.base import CaptionModel, CaptionResult


class BLIPCaptionModel(CaptionModel):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = BlipProcessor.from_pretrained(settings.blip_model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(
            settings.blip_model_name
        ).to(self.device)
        self.model.eval()
        self._initialized = True

    def generate_caption(
        self,
        image: Image.Image,
        style: str = "descriptive",
        context: str = "",
    ) -> CaptionResult:
        start = time.time()

        image_rgb = image.convert("RGB")

        prompt = self._get_prompt(style)
        if prompt:
            inputs = self.processor(image_rgb, prompt, return_tensors="pt").to(
                self.device
            )
        else:
            inputs = self.processor(image_rgb, return_tensors="pt").to(self.device)

        num_beams = 3 if self.device == "cuda" else 1
        with torch.no_grad():
            output = self.model.generate(
                **inputs, max_new_tokens=80, num_beams=num_beams, early_stopping=True
            )

        caption = self.processor.decode(output[0], skip_special_tokens=True)

        if prompt and caption.lower().startswith(prompt.lower()):
            caption = caption[len(prompt) :].strip()

        latency = (time.time() - start) * 1000

        return CaptionResult(
            caption=caption,
            model_name=self.get_model_name(),
            tier=self.get_tier(),
            latency_ms=latency,
            cost_usd=0.0,
        )

    def _get_prompt(self, style: str) -> str:
        prompts = {
            "descriptive": "a detailed photograph of",
            "creative": "an artistic image showing",
            "technical": "a technical description of",
            "concise": "",
            "social_media": "a photo of",
        }
        return prompts.get(style, "")

    def get_tier(self) -> int:
        return 1

    def get_model_name(self) -> str:
        return "BLIP"
