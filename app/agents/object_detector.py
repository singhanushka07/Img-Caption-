from __future__ import annotations

from collections import defaultdict

import PIL.Image
from ultralytics import YOLO

from app.config import settings


class ObjectDetector:
    _instance: ObjectDetector | None = None
    _initialized: bool = False

    def __new__(cls) -> ObjectDetector:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.model = YOLO(settings.yolo_model_name)
        ObjectDetector._initialized = True

    def detect(self, image: PIL.Image.Image) -> list[dict]:
        try:
            results = self.model(image, verbose=False)
            aggregated: dict[str, dict] = defaultdict(
                lambda: {"confidence": 0.0, "count": 0}
            )
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf < settings.yolo_confidence_threshold:
                        continue
                    label = result.names[int(box.cls[0])]
                    entry = aggregated[label]
                    entry["count"] += 1
                    if conf > entry["confidence"]:
                        entry["confidence"] = conf
            detections = [
                {"label": label, "confidence": data["confidence"], "count": data["count"]}
                for label, data in aggregated.items()
            ]
            detections.sort(key=lambda d: d["confidence"], reverse=True)
            return detections
        except Exception:
            return []

    @staticmethod
    def format_context(detections: list[dict]) -> str:
        if not detections:
            return ""
        parts = []
        for d in detections:
            label = f"{d['count']} {d['label']}s" if d["count"] > 1 else f"{d['count']} {d['label']}"
            parts.append(f"{label} ({d['confidence']:.2f})")
        return "Detected objects: " + ", ".join(parts)


_detector: ObjectDetector | None = None


def get_object_detector() -> ObjectDetector:
    global _detector
    if _detector is None:
        _detector = ObjectDetector()
    return _detector
