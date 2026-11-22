import pytest
from PIL import Image
from unittest.mock import patch, MagicMock

from app.models.base import CaptionResult


def _make_test_image():
    return Image.new("RGB", (224, 224), color=(128, 128, 128))


class TestCaptionResult:
    def test_defaults(self):
        result = CaptionResult(
            caption="a test image",
            model_name="test",
            tier=1,
        )
        assert result.caption == "a test image"
        assert result.cost_usd == 0.0
        assert result.metadata == {}

    def test_with_metadata(self):
        result = CaptionResult(
            caption="test",
            model_name="gpt-4o",
            tier=3,
            cost_usd=0.01,
            metadata={"tokens": 100},
        )
        assert result.metadata["tokens"] == 100


class TestBLIPModel:
    @patch("app.models.blip_model.BlipForConditionalGeneration")
    @patch("app.models.blip_model.BlipProcessor")
    def test_generate_caption(self, mock_processor_cls, mock_model_cls):
        mock_processor = MagicMock()
        mock_processor_cls.from_pretrained.return_value = mock_processor
        mock_inputs = MagicMock()
        mock_processor.return_value = mock_inputs
        mock_processor.decode.return_value = "a gray test image"

        mock_model = MagicMock()
        mock_model_cls.from_pretrained.return_value = mock_model
        mock_model.generate.return_value = [MagicMock()]

        from app.models.blip_model import BLIPCaptionModel

        BLIPCaptionModel._instance = None
        model = BLIPCaptionModel()

        image = _make_test_image()
        result = model.generate_caption(image, style="concise")

        assert isinstance(result, CaptionResult)
        assert result.tier == 1
        assert result.cost_usd == 0.0
        assert result.model_name == "BLIP"


class TestOpenAIModel:
    @patch("app.models.openai_model.OpenAI")
    def test_generate_caption(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "A detailed image description"
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 120
        mock_client.chat.completions.create.return_value = mock_response

        from app.models.openai_model import OpenAICaptionModel

        model = OpenAICaptionModel("gpt-4o-mini")
        image = _make_test_image()
        result = model.generate_caption(image, style="descriptive")

        assert isinstance(result, CaptionResult)
        assert result.tier == 2
        assert result.caption == "A detailed image description"
        assert result.cost_usd > 0
