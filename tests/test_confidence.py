import pytest
from unittest.mock import patch

from app.agents.confidence import compute_confidence, generate_explanation


class TestConfidence:
    @patch("app.agents.confidence.settings")
    def test_high_confidence(self, mock_settings):
        mock_settings.clip_score_threshold = 0.25
        mock_settings.confidence_clip_weight = 0.5
        mock_settings.confidence_judge_weight = 0.5

        critic_result = {
            "clip_score": 0.35,
            "judge_scores": {"overall": 9, "reason": "Excellent match"},
        }
        score, explanation = compute_confidence(critic_result)
        assert score >= 85

    @patch("app.agents.confidence.settings")
    def test_low_confidence(self, mock_settings):
        mock_settings.clip_score_threshold = 0.25
        mock_settings.confidence_clip_weight = 0.5
        mock_settings.confidence_judge_weight = 0.5

        critic_result = {
            "clip_score": 0.1,
            "judge_scores": {"overall": 3, "reason": "Poor match"},
        }
        score, explanation = compute_confidence(critic_result)
        assert score < 60

    @patch("app.agents.confidence.settings")
    def test_score_range(self, mock_settings):
        mock_settings.clip_score_threshold = 0.25
        mock_settings.confidence_clip_weight = 0.5
        mock_settings.confidence_judge_weight = 0.5

        for clip, judge in [(0.0, 0), (0.5, 10), (0.25, 5)]:
            critic_result = {
                "clip_score": clip,
                "judge_scores": {"overall": judge},
            }
            score, _ = compute_confidence(critic_result)
            assert 0 <= score <= 100

    @patch("app.agents.confidence.settings")
    def test_explanation_high(self, mock_settings):
        mock_settings.clip_score_threshold = 0.25
        mock_settings.confidence_clip_weight = 0.5
        mock_settings.confidence_judge_weight = 0.5

        critic_result = {
            "clip_score": 0.35,
            "judge_scores": {"overall": 9, "reason": ""},
        }
        score, explanation = compute_confidence(critic_result)
        assert score >= 85
        assert "High confidence" in explanation

    @patch("app.agents.confidence.settings")
    def test_explanation_low(self, mock_settings):
        mock_settings.clip_score_threshold = 0.25
        mock_settings.confidence_clip_weight = 0.5
        mock_settings.confidence_judge_weight = 0.5

        critic_result = {
            "clip_score": 0.1,
            "judge_scores": {"overall": 3, "reason": ""},
        }
        score, explanation = compute_confidence(critic_result)
        assert score < 60
        assert "Low confidence" in explanation
