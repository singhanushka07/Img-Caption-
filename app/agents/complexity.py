import numpy as np
import cv2
from PIL import Image


class ImageComplexityAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

    def analyze(self, image: Image.Image) -> dict:
        try:
            img_array = np.array(image.convert("RGB"))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

            edges = cv2.Canny(gray, 100, 200)
            edge_density = float(np.count_nonzero(edges)) / edges.size

            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            color_variance = float(np.std(hsv[:, :, :2]))
            color_variance = min(color_variance / 80.0, 1.0)

            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            texture_score = min(float(laplacian_var) / 500.0, 1.0)

            complexity_score = (
                edge_density * 0.4 + color_variance * 0.3 + texture_score * 0.3
            )
            complexity_score = min(complexity_score, 1.0)

            if complexity_score < 0.3:
                label = "simple"
            elif complexity_score <= 0.6:
                label = "medium"
            else:
                label = "complex"

            return {
                "complexity_score": complexity_score,
                "complexity_label": label,
                "metrics": {
                    "edge_density": edge_density,
                    "color_variance": color_variance,
                    "texture_score": texture_score,
                },
            }
        except Exception:
            return {
                "complexity_score": 0.5,
                "complexity_label": "medium",
                "metrics": {
                    "edge_density": 0.0,
                    "color_variance": 0.0,
                    "texture_score": 0.0,
                },
            }


_analyzer = None


def get_complexity_analyzer() -> ImageComplexityAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = ImageComplexityAnalyzer()
    return _analyzer
