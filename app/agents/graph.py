from langgraph.graph import StateGraph, END

from app.agents.state import CaptionState
from app.agents.router import route_node
from app.agents.caption_agent import generate_caption_node
from app.agents.critic_agent import CriticAgent
from app.agents.confidence import compute_confidence

_critic = None


def _get_critic() -> CriticAgent:
    global _critic
    if _critic is None:
        _critic = CriticAgent()
    return _critic


def detect_objects_node(state: CaptionState) -> CaptionState:
    from app.agents.object_detector import get_object_detector, ObjectDetector

    image = state.get("image")
    if image is None:
        return {"detected_objects": [], "object_context": ""}

    detector = get_object_detector()
    detections = detector.detect(image)
    context = ObjectDetector.format_context(detections)
    return {"detected_objects": detections, "object_context": context}


def critique_node(state: CaptionState) -> CaptionState:
    critic = _get_critic()
    image = state["image"]
    caption = state["caption"]
    style = state.get("style", "descriptive")

    result = critic.evaluate(image, caption, style)

    score, explanation = compute_confidence(result)
    return {
        "critic_result": result,
        "confidence_score": score,
        "confidence_explanation": explanation,
    }


def refine_node(state: CaptionState) -> CaptionState:
    from app.agents.refinement_agent import get_refinement_agent

    caption = state.get("caption", "")
    agent = get_refinement_agent()
    refinements = agent.refine(caption)
    return {"refinements": refinements}


def escalate_node(state: CaptionState) -> CaptionState:
    current_tier = state.get("current_tier", 1)
    next_tier = min(current_tier + 1, 3)
    return {
        "current_tier": next_tier,
        "escalation_count": state.get("escalation_count", 0) + 1,
    }


def should_escalate(state: CaptionState) -> str:
    critic_result = state.get("critic_result", {})
    current_tier = state.get("current_tier", 1)
    escalation_count = state.get("escalation_count", 0)

    if critic_result.get("passes", False):
        return "accept"

    if current_tier >= 3 or escalation_count >= 2:
        return "accept"

    return "escalate"


def build_caption_graph() -> StateGraph:
    graph = StateGraph(CaptionState)

    graph.add_node("route", route_node)
    graph.add_node("detect_objects", detect_objects_node)
    graph.add_node("generate", generate_caption_node)
    graph.add_node("critique", critique_node)
    graph.add_node("refine", refine_node)
    graph.add_node("escalate", escalate_node)

    graph.set_entry_point("route")
    graph.add_edge("route", "detect_objects")
    graph.add_edge("detect_objects", "generate")
    graph.add_edge("generate", "critique")

    graph.add_conditional_edges(
        "critique",
        should_escalate,
        {
            "accept": "refine",
            "escalate": "escalate",
        },
    )

    graph.add_edge("refine", END)
    graph.add_edge("escalate", "generate")

    return graph.compile()

caption_workflow = None


def get_caption_workflow():
    global caption_workflow
    if caption_workflow is None:
        caption_workflow = build_caption_graph()
    return caption_workflow
