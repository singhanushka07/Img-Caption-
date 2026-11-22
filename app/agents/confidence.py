from app.config import settings


def generate_explanation(score: float, critic_result: dict) -> str:
    clip_score = critic_result.get("clip_score", 0.0)
    judge_scores = critic_result.get("judge_scores", {})
    overall = judge_scores.get("overall", 5)
    reason = judge_scores.get("reason", "")

    if score >= 85:
        explanation = (
            f"High confidence. The caption closely matches the image content "
            f"(CLIP: {clip_score:.3f}) and received strong quality ratings ({overall}/10)."
        )
    elif score >= 60:
        if reason and reason.lower() not in ("none", "n/a", "error", "no reason provided"):
            explanation = f"Moderate confidence. {reason}"
        else:
            explanation = (
                "Moderate confidence. The caption adequately describes the image "
                "but has room for improvement."
            )
    else:
        base = "Low confidence. The caption may not fully capture the image content."
        if reason and reason.lower() not in ("none", "n/a", "error", "no reason provided"):
            explanation = f"{base} {reason}"
        else:
            explanation = base

    return explanation


def compute_confidence(critic_result: dict) -> tuple[float, str]:
    clip_score = critic_result["clip_score"]
    judge_overall = critic_result.get("judge_scores", {}).get("overall", 5)

    clip_norm = min(clip_score / max(settings.clip_score_threshold, 0.01), 1.0) * 100
    judge_norm = (judge_overall / 10) * 100

    score = settings.confidence_clip_weight * clip_norm + settings.confidence_judge_weight * judge_norm
    score = round(max(0.0, min(100.0, score)), 1)

    explanation = generate_explanation(score, critic_result)
    return score, explanation
