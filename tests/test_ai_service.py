"""
Unit tests for AIService (Gemini integration logic and fallbacks).
"""

from src.services.ai_service import AIService


def test_ai_service_without_api_key():
    service = AIService(api_key="")
    success, msg = service.test_connection()
    assert success is False
    assert "missing" in msg.lower() or "not configured" in msg.lower()

    success, prompt = service.generate_prompt(category="story")
    assert success is False
    assert "not configured" in prompt.lower()


def test_ai_feedback_validation_short_text():
    service = AIService(api_key="mock_key")
    success, feedback = service.get_writing_feedback(text="Too short", category="story")
    assert success is False
    assert "at least a few sentences" in feedback.lower()


def test_ai_service_set_key():
    service = AIService(api_key="")
    assert service.api_key == ""
    service.set_api_key("test_new_key_123")
    assert service.api_key == "test_new_key_123"
