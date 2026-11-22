import pytest
from unittest.mock import patch, MagicMock
from PIL import Image

from app.agents.object_detector import ObjectDetector


def _make_test_image():
    return Image.new("RGB", (224, 224), color=(128, 128, 128))


class TestObjectDetector:
    def test_format_context_empty(self):
        result = ObjectDetector.format_context([])
        assert result == ""

    def test_format_context_single(self):
        detections = [{"label": "dog", "confidence": 0.92, "count": 1}]
        result = ObjectDetector.format_context(detections)
        assert result == "Detected objects: 1 dog (0.92)"

    def test_format_context_plural(self):
        detections = [{"label": "dog", "confidence": 0.92, "count": 2}]
        result = ObjectDetector.format_context(detections)
        assert "2 dogs" in result

    @patch("app.agents.object_detector.YOLO")
    @patch("app.agents.object_detector.settings")
    def test_detect_with_mock(self, mock_settings, mock_yolo_cls):
        mock_settings.yolo_model_name = "yolov8n.pt"
        mock_settings.yolo_confidence_threshold = 0.3

        mock_box1 = MagicMock()
        mock_box1.conf = [0.95]
        mock_box1.cls = [16]

        mock_box2 = MagicMock()
        mock_box2.conf = [0.88]
        mock_box2.cls = [16]

        mock_result = MagicMock()
        mock_result.boxes = [mock_box1, mock_box2]
        mock_result.names = {16: "dog"}

        mock_model = MagicMock()
        mock_model.return_value = [mock_result]
        mock_yolo_cls.return_value = mock_model

        ObjectDetector._instance = None
        ObjectDetector._initialized = False
        detector = ObjectDetector()
        detections = detector.detect(_make_test_image())

        assert len(detections) == 1
        assert detections[0]["label"] == "dog"
        assert detections[0]["count"] == 2
        assert detections[0]["confidence"] == 0.95
