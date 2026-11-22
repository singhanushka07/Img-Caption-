from openai import OpenAI
from PIL import Image

from app.config import settings


class RefinementAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.has_openai else None

    def refine(self, caption: str) -> dict:
        if self.client is None:
            return {"alt_text": caption, "seo": caption}

        try:
            alt_resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You generate accessible alt-text for images."},
                    {
                        "role": "user",
                        "content": (
                            "Rewrite this image caption as accessible alt-text for screen readers. "
                            "Be concise, factual, describe the main subject first. Under 125 characters.\n\n"
                            f"Caption: {caption}"
                        ),
                    },
                ],
                max_tokens=80,
                temperature=0.3,
            )
            alt_text = alt_resp.choices[0].message.content.strip()
        except Exception:
            alt_text = caption

        try:
            seo_resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You optimize image captions for search engines."},
                    {
                        "role": "user",
                        "content": (
                            "Rewrite this image caption as an SEO-optimized meta description. "
                            "Include relevant keywords naturally. Under 160 characters.\n\n"
                            f"Caption: {caption}"
                        ),
                    },
                ],
                max_tokens=100,
                temperature=0.4,
            )
            seo = seo_resp.choices[0].message.content.strip()
        except Exception:
            seo = caption

        return {"alt_text": alt_text, "seo": seo}


_agent = None


def get_refinement_agent() -> RefinementAgent:
    global _agent
    if _agent is None:
        _agent = RefinementAgent()
    return _agent
