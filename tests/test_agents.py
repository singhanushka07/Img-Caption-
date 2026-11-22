import pytest
from unittest.mock import patch, MagicMock
from PIL import Image

from app.agents.state import CaptionState
from app.agents.router import route_node
from app.agents.graph import detect_objects_node


def _make_test_image():
    return Image.new("RGB", (224, 224), color=(128, 128, 128))


class TestRouteNode:
    @patch("app.agents.router.get_rag_memory")
    def test_initial_routing(self, mock_rag):
        mock_memory = MagicMock()
        mock_memory.get_context_string.return_value = ""
        mock_rag.return_value = mock_memory

        state = {"image": _make_test_image(), "style": "descriptive"}
        result = route_node(state)

        assert result["current_tier"] == 1
        assert result["escalation_count"] == 0
        assert result["total_cost"] == 0.0


    @patch("app.agents.router.get_complexity_analyzer")
    @patch("app.agents.router.get_rag_memory")
    def test_returns_complexity_fields(self, mock_rag, mock_analyzer):
        mock_memory = MagicMock()
        mock_memory.get_context_string.return_value = ""
        mock_rag.return_value = mock_memory

        mock_complexity = MagicMock()
        mock_complexity.analyze.return_value = {
            "complexity_score": 0.75,
            "complexity_label": "complex",
            "metrics": {
                "edge_density": 0.3,
                "color_variance": 0.6,
                "texture_score": 0.8,
            },
        }
        mock_analyzer.return_value = mock_complexity

        state = {"image": _make_test_image(), "style": "descriptive"}
        result = route_node(state)

        assert result["complexity_score"] == 0.75
        assert result["complexity_label"] == "complex"


class TestDetectObjectsNode:
    @patch("app.agents.graph.get_object_detector")
    def test_detect_objects_node(self, mock_get_detector):
        mock_detector = MagicMock()
        mock_detector.detect.return_value = [
            {"label": "cat", "confidence": 0.95, "count": 1}
        ]
        mock_get_detector.return_value = mock_detector

        state = {"image": _make_test_image()}
        result = detect_objects_node(state)

        assert result["detected_objects"] == [
            {"label": "cat", "confidence": 0.95, "count": 1}
        ]
        assert "Detected objects:" in result["object_context"]
        mock_detector.detect.assert_called_once()

    def test_detect_objects_node_no_image(self):
        state = {"image": None}
        result = detect_objects_node(state)
        assert result["detected_objects"] == []
        assert result["object_context"] == ""


class TestGraphFlow:
    def test_should_escalate_on_pass(self):
        from app.agents.graph import should_escalate

        state = {
            "critic_result": {"passes": True},
            "current_tier": 1,
        }
        assert should_escalate(state) == "accept"

    def test_should_escalate_on_fail(self):
        from app.agents.graph import should_escalate

        state = {
            "critic_result": {"passes": False},
            "current_tier": 1,
        }
        assert should_escalate(state) == "escalate"

    def test_should_accept_at_max_tier(self):
        from app.agents.graph import should_escalate

        state = {
            "critic_result": {"passes": False},
            "current_tier": 3,
        }
        assert should_escalate(state) == "accept"

    def test_escalate_increments_tier(self):
        from app.agents.graph import escalate_node

        state = {"current_tier": 1, "escalation_count": 0}
        result = escalate_node(state)
        assert result["current_tier"] == 2
        assert result["escalation_count"] == 1
