import pytest
from unittest.mock import patch, MagicMock

from app.agents.refinement_agent import RefinementAgent


class TestRefinementAgent:
    @patch("app.agents.refinement_agent.settings")
    def test_offline_returns_original(self, mock_settings):
        mock_settings.has_openai = False
        mock_settings.openai_api_key = ""

        agent = RefinementAgent()
        result = agent.refine("hello")

        assert result == {"alt_text": "hello", "seo": "hello"}

    @patch("app.agents.refinement_agent.OpenAI")
    @patch("app.agents.refinement_agent.settings")
    def test_refine_with_mock(self, mock_settings, mock_openai_cls):
        mock_settings.has_openai = True
        mock_settings.openai_api_key = "sk-test"

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_alt_resp = MagicMock()
        mock_alt_resp.choices = [MagicMock()]
        mock_alt_resp.choices[0].message.content = "Alt: a gray image"

        mock_seo_resp = MagicMock()
        mock_seo_resp.choices = [MagicMock()]
        mock_seo_resp.choices[0].message.content = "SEO: gray image description"

        mock_client.chat.completions.create.side_effect = [
            mock_alt_resp,
            mock_seo_resp,
        ]

        agent = RefinementAgent()
        result = agent.refine("a gray test image")

        assert result["alt_text"] == "Alt: a gray image"
        assert result["seo"] == "SEO: gray image description"

    @patch("app.agents.refinement_agent.OpenAI")
    @patch("app.agents.refinement_agent.settings")
    def test_partial_failure(self, mock_settings, mock_openai_cls):
        mock_settings.has_openai = True
        mock_settings.openai_api_key = "sk-test"

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_alt_resp = MagicMock()
        mock_alt_resp.choices = [MagicMock()]
        mock_alt_resp.choices[0].message.content = "Custom alt text"

        mock_client.chat.completions.create.side_effect = [
            mock_alt_resp,
            Exception("API error"),
        ]

        agent = RefinementAgent()
        result = agent.refine("original caption")

        assert result["alt_text"] == "Custom alt text"
        assert result["seo"] == "original caption"
