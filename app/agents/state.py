from typing import TypedDict, Any, Optional
from PIL import Image


class CaptionState(TypedDict, total=False):
    image: Any  # PIL Image (not serializable, passed by reference)
    image_bytes: bytes
    style: str
    current_tier: int
    caption: str
    critic_result: dict
    escalation_count: int
    total_cost: float
    total_latency: float
    rag_context: str
    history: list[dict]
    final: bool

    complexity_score: float
    complexity_label: str
    detected_objects: list[dict]
    object_context: str
    refinements: dict
    language: str
    translated_caption: str
    confidence_score: float
    confidence_explanation: str
