import pytest
from unittest.mock import patch, MagicMock

from app.agents.translation import translate_caption


class TestTranslation:
    def test_english_passthrough(self):
        result = translate_caption("hello", "English")
        assert result == "hello"

    def test_empty_language_passthrough(self):
        result = translate_caption("hello", "")
        assert result == "hello"

    @patch("app.agents.translation.settings")
    @patch("app.agents.translation._get_client")
    def test_offline_returns_original(self, mock_get_client, mock_settings):
        mock_settings.has_openai = False
        mock_get_client.return_value = None

        result = translate_caption("hello", "Spanish")
        assert result == "hello"

    @patch("app.agents.translation._get_client")
    def test_translate_with_mock(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "hola"
        mock_client.chat.completions.create.return_value = mock_response

        result = translate_caption("hello", "Spanish")
        assert result == "hola"
