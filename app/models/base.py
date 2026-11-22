from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from PIL import Image


@dataclass
class CaptionResult:
    caption: str
    model_name: str
    tier: int
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    tokens_used: int = 0
    metadata: dict = field(default_factory=dict)


class CaptionModel(ABC):
    @abstractmethod
    def generate_caption(
        self,
        image: Image.Image,
        style: str = "descriptive",
        context: str = "",
    ) -> CaptionResult:
        pass

    @abstractmethod
    def get_tier(self) -> int:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass
