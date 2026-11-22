from app.agents.state import CaptionState
from app.config import settings
from app.models.blip_model import BLIPCaptionModel
from app.models.openai_model import OpenAICaptionModel

_blip_model = None
_openai_mini = None
_openai_4o = None


def _get_model(tier: int):
    global _blip_model, _openai_mini, _openai_4o
    if tier <= 1:
        if _blip_model is None:
            _blip_model = BLIPCaptionModel()
        return _blip_model
    elif tier == 2:
        if _openai_mini is None:
            _openai_mini = OpenAICaptionModel("gpt-4o-mini")
        return _openai_mini
    else:  # tier 3 or anything higher — cap at gpt-4o
        if _openai_4o is None:
            _openai_4o = OpenAICaptionModel("gpt-4o")
        return _openai_4o


def generate_caption_node(state: CaptionState) -> CaptionState:
    tier = state.get("current_tier", 1)
    image = state["image"]
    style = state.get("style", "descriptive")
    rag_context = state.get("rag_context", "")
    object_context = state.get("object_context", "")
    context = rag_context + ("\n" + object_context if object_context else "")

    # Offline-first: fall back to BLIP if no API key is configured
    if tier > 1 and not settings.has_openai:
        tier = 1

    try:
        model = _get_model(tier)
        result = model.generate_caption(image, style=style, context=context)
    except Exception as exc:
        if tier == 1 and settings.has_openai:
            # BLIP failed or downloading — escalate directly to Tier 2 (OpenAI)
            tier = 2
            model = _get_model(2)
            result = model.generate_caption(image, style=style, context=context)
        elif tier > 1:
            # OpenAI call failed — fall back to BLIP
            try:
                tier = 1
                model = _get_model(1)
                result = model.generate_caption(image, style=style, context=context)
            except Exception:
                raise exc
        else:
            raise

    history = list(state.get("history", []))
    history.append(
        {
            "tier": tier,
            "model": result.model_name,
            "caption": result.caption,
            "cost": result.cost_usd,
            "latency_ms": result.latency_ms,
        }
    )

    return {
        "caption": result.caption,
        "current_tier": tier,
        "total_cost": state.get("total_cost", 0.0) + result.cost_usd,
        "total_latency": state.get("total_latency", 0.0) + result.latency_ms,
        "history": history,
    }
