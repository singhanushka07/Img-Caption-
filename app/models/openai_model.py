import base64
import io
import time
from PIL import Image
from openai import OpenAI

from app.config import settings
from app.models.base import CaptionModel, CaptionResult
from app.styles.prompts import get_style_prompt

PRICING = {
    "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
}


class OpenAICaptionModel(CaptionModel):
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.tier = 2 if model_name == "gpt-4o-mini" else 3

    def generate_caption(
        self,
        image: Image.Image,
        style: str = "descriptive",
        context: str = "",
    ) -> CaptionResult:
        start = time.time()

        base64_image = self._encode_image(image)
        style_prompt = get_style_prompt(style)

        system_msg = (
            "You are an expert image captioning assistant. "
            "Generate high-quality captions based on the given style instructions."
        )

        user_content = []

        if context:
            user_content.append(
                {
                    "type": "text",
                    "text": f"Reference captions for context:\n{context}\n\n",
                }
            )

        user_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "high" if self.tier == 3 else "low",
                },
            }
        )

        user_content.append(
            {
                "type": "text",
                "text": style_prompt,
            }
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_content},
            ],
            max_tokens=300,
            temperature=0.7,
            timeout=25.0,
        )

        caption = response.choices[0].message.content.strip()
        usage = response.usage

        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        pricing = PRICING.get(self.model_name, PRICING["gpt-4o-mini"])
        cost = (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])

        latency = (time.time() - start) * 1000

        return CaptionResult(
            caption=caption,
            model_name=self.get_model_name(),
            tier=self.get_tier(),
            latency_ms=latency,
            cost_usd=cost,
            tokens_used=total_tokens,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )

    def _encode_image(self, image: Image.Image) -> str:
        image_rgb = image.convert("RGB")
        buffer = io.BytesIO()
        image_rgb.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def get_tier(self) -> int:
        return self.tier

    def get_model_name(self) -> str:
        return self.model_name
