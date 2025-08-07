import pytest
from src.services.conversation_service import ConversationService


def test_is_conversational_query():
    service = ConversationService()
    assert service.is_conversational_query("hello") is True
    assert service.is_conversational_query("hi there") is True
    assert service.is_conversational_query("how are you") is True
    assert service.is_conversational_query("select * from users") is False


def test_get_conversational_response():
    service = ConversationService()
    response = service.get_conversational_response("hello")
    assert response is not None
    assert len(response) > 0
    assert "hello" in response.lower() or "hi" in response.lower()


def test_get_conversational_response_help():
    service = ConversationService()
    response = service.get_conversational_response("what can you do?")
    assert "SQL" in response
    assert "data analysis" in response.lower()


def test_get_conversational_response_thanks():
    service = ConversationService()
    response = service.get_conversational_response("thank you")
    assert "help you today" in response.lower()
