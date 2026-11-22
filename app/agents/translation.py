from app.config import settings
from openai import OpenAI

_client = None


def _get_client():
    global _client
    if _client is None and settings.has_openai:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def translate_caption(caption: str, target_language: str) -> str:
    if target_language in ("English", ""):
        return caption

    client = _get_client()
    if client is None:
        return caption

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate accurately, preserving tone and meaning. Return only the translated text.",
                },
                {
                    "role": "user",
                    "content": f"Translate the following image caption to {target_language}:\n\n{caption}",
                },
            ],
            max_tokens=300,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return caption
