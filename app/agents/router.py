from app.agents.state import CaptionState
from app.rag.memory import RAGMemory
from app.agents.complexity import get_complexity_analyzer
from app.config import settings


_rag_memory = None


def get_rag_memory() -> RAGMemory:
    global _rag_memory
    if _rag_memory is None:
        _rag_memory = RAGMemory()
    return _rag_memory


def route_node(state: CaptionState) -> CaptionState:
    rag = get_rag_memory()
    style = state.get("style", "descriptive")
    image = state.get("image")

    context = rag.get_context_string(
        f"image caption in {style} style", style=style, image=image,
    )

    analyzer = get_complexity_analyzer()
    complexity = analyzer.analyze(image) if image else {
        "complexity_score": 0.5, "complexity_label": "medium",
    }

    starting_tier = 1
    if complexity["complexity_label"] == "complex" and settings.has_openai:
        starting_tier = 2

    return {
        "current_tier": starting_tier,
        "escalation_count": 0,
        "total_cost": 0.0,
        "total_latency": 0.0,
        "rag_context": context,
        "history": [],
        "final": False,
        "complexity_score": complexity["complexity_score"],
        "complexity_label": complexity["complexity_label"],
    }
