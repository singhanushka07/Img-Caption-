import mlflow
from app.config import settings
from app.tracking import local_tracker


class CaptionTracker:
    def __init__(self):
        self.experiment_name = "image-captioning"
        try:
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            mlflow.set_experiment(self.experiment_name)
        except Exception:
            pass

    def log_caption_run(
        self,
        model_name: str,
        style: str,
        caption: str,
        clip_score: float,
        judge_score: int,
        latency_ms: float,
        cost_usd: float,
        escalation_count: int,
        tier_used: int,
        image_hash: str = "",
    ):
        local_tracker.log_run(
            model_name=model_name,
            style=style,
            tier_used=tier_used,
            clip_score=clip_score,
            judge_score=judge_score,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            escalation_count=escalation_count,
            caption_length=len(caption),
            image_hash=image_hash,
        )
        try:
            self._mlflow_log(
                model_name, style, caption, clip_score, judge_score,
                latency_ms, cost_usd, escalation_count, tier_used, image_hash,
            )
        except Exception:
            pass  # MLflow is optional

    def _mlflow_log(
        self,
        model_name, style, caption, clip_score, judge_score,
        latency_ms, cost_usd, escalation_count, tier_used, image_hash,
    ):
        with mlflow.start_run():
            mlflow.log_params(
                {
                    "model_name": model_name,
                    "style": style,
                    "tier_used": tier_used,
                    "image_hash": image_hash[:8] if image_hash else "unknown",
                }
            )
            mlflow.log_metrics(
                {
                    "clip_score": clip_score,
                    "judge_score": judge_score,
                    "latency_ms": latency_ms,
                    "cost_usd": cost_usd,
                    "escalation_count": escalation_count,
                    "caption_length": len(caption),
                }
            )
            mlflow.log_text(caption, "caption.txt")

    def get_experiment_stats(self) -> dict:
        return local_tracker.get_stats()
