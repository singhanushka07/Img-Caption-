import io
import base64
from PIL import Image
from openai import OpenAI

from app.config import settings

_SYSTEM = (
    "You are a highly capable visual question-answering assistant. "
    "Answer questions about the provided image accurately, concisely, and helpfully. "
    "Leverage the full conversation history for context."
)


class VQAConversation:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.has_openai else None
        # session_id → list of {"question": str, "answer": str}
        self.sessions: dict[str, list[dict]] = {}
        # session_id → base64 image (refreshed each call so new images work)
        self._images: dict[str, str] = {}

    def ask(self, session_id: str, image: Image.Image, question: str) -> dict:
        if not self.client:
            return {
                "answer": "OpenAI API key is not configured. VQA requires GPT-4o-mini.",
                "tokens_used": 0,
                "history_length": 0,
            }

        b64 = self._encode_image(image)
        self._images[session_id] = b64

        history = self.sessions.setdefault(session_id, [])
        messages = [{"role": "system", "content": _SYSTEM}]

        if not history:
            # First turn: send image at high detail with the question
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"},
                    },
                    {"type": "text", "text": question},
                ],
            })
        else:
            # Replay history: first msg uses low-detail image to save tokens
            first = history[0]
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"},
                    },
                    {"type": "text", "text": first["question"]},
                ],
            })
            messages.append({"role": "assistant", "content": first["answer"]})

            for entry in history[1:]:
                messages.append({"role": "user", "content": entry["question"]})
                messages.append({"role": "assistant", "content": entry["answer"]})

            messages.append({"role": "user", "content": question})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.5,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as exc:
            return {
                "answer": f"OpenAI API error: {exc}. Check your API key and quota.",
                "tokens_used": 0,
                "history_length": len(history),
            }

        history.append({"question": question, "answer": answer})

        return {
            "answer": answer,
            "tokens_used": response.usage.total_tokens,
            "history_length": len(history),
        }

    def clear_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)
        self._images.pop(session_id, None)

    @staticmethod
    def _encode_image(image: Image.Image) -> str:
        image_rgb = image.convert("RGB")
        buf = io.BytesIO()
        image_rgb.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
