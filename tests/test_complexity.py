import pytest
import numpy as np
from PIL import Image

from app.agents.complexity import ImageComplexityAnalyzer, get_complexity_analyzer


def _make_solid_image():
    return Image.new("RGB", (224, 224), color=(128, 128, 128))


def _make_noisy_image():
    rng = np.random.RandomState(42)
    data = rng.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    return Image.fromarray(data)


class TestImageComplexityAnalyzer:
    def test_simple_image(self):
        analyzer = ImageComplexityAnalyzer()
        result = analyzer.analyze(_make_solid_image())

        assert result["complexity_label"] == "simple"
        assert result["complexity_score"] < 0.3

    def test_complex_image(self):
        analyzer = ImageComplexityAnalyzer()
        result = analyzer.analyze(_make_noisy_image())

        assert result["complexity_label"] in ("complex", "medium")
        assert result["complexity_score"] > 0.3

    def test_returns_all_keys(self):
        analyzer = ImageComplexityAnalyzer()
        result = analyzer.analyze(_make_solid_image())

        assert "complexity_score" in result
        assert "complexity_label" in result
        assert "metrics" in result
        metrics = result["metrics"]
        assert "edge_density" in metrics
        assert "color_variance" in metrics
        assert "texture_score" in metrics

    def test_score_range(self):
        analyzer = ImageComplexityAnalyzer()

        for img in [_make_solid_image(), _make_noisy_image()]:
            result = analyzer.analyze(img)
            assert 0.0 <= result["complexity_score"] <= 1.0

    def test_singleton(self):
        a = get_complexity_analyzer()
        b = get_complexity_analyzer()
        assert a is b
