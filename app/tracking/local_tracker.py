"""
JSON-based run tracker for real-time dashboard analytics.
Writes one JSON line per captioning run to data/runs.jsonl.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

_RUNS_FILE = Path("./data/runs.jsonl")


def _ensure():
    _RUNS_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_run(
    *,
    model_name: str,
    style: str,
    tier_used: int,
    clip_score: float,
    judge_score: int,
    latency_ms: float,
    cost_usd: float,
    escalation_count: int,
    caption_length: int,
    image_hash: str = "",
) -> None:
    _ensure()
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model_name,
        "style": style,
        "tier": tier_used,
        "clip_score": round(clip_score, 6),
        "judge_score": judge_score,
        "latency_ms": round(latency_ms, 1),
        "cost_usd": round(cost_usd, 8),
        "escalations": escalation_count,
        "caption_len": caption_length,
        "img_hash": image_hash[:8] if image_hash else "",
    }
    with open(_RUNS_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def load_runs() -> list[dict]:
    if not _RUNS_FILE.exists():
        return []
    out = []
    with open(_RUNS_FILE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def get_stats() -> dict:
    runs = load_runs()
    empty = {
        "total_runs": 0,
        "avg_cost": 0.0,
        "avg_latency": 0.0,
        "avg_clip_score": 0.0,
        "avg_judge_score": 0.0,
        "total_cost": 0.0,
        "avg_escalations": 0.0,
        "model_usage": {},
        "style_usage": {},
        "tier_usage": {},
        "recent_runs": [],
    }
    if not runs:
        return empty

    n = len(runs)
    model_usage: dict[str, int] = {}
    style_usage: dict[str, int] = {}
    tier_usage: dict[str, int] = {}

    for r in runs:
        model_usage[r.get("model", "?")] = model_usage.get(r.get("model", "?"), 0) + 1
        style_usage[r.get("style", "?")] = style_usage.get(r.get("style", "?"), 0) + 1
        t = str(r.get("tier", 0))
        tier_usage[t] = tier_usage.get(t, 0) + 1

    return {
        "total_runs": n,
        "avg_cost": sum(r.get("cost_usd", 0) for r in runs) / n,
        "avg_latency": sum(r.get("latency_ms", 0) for r in runs) / n,
        "avg_clip_score": sum(r.get("clip_score", 0) for r in runs) / n,
        "avg_judge_score": sum(r.get("judge_score", 0) for r in runs) / n,
        "total_cost": sum(r.get("cost_usd", 0) for r in runs),
        "avg_escalations": sum(r.get("escalations", 0) for r in runs) / n,
        "model_usage": model_usage,
        "style_usage": style_usage,
        "tier_usage": tier_usage,
        "recent_runs": runs[-50:],
    }
