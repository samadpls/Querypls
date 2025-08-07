import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.schemas.requests import ChatMessage, NewChatRequest, SQLGenerationRequest
from src.schemas.responses import ChatResponse, SessionInfo


def test_chat_message():
    msg = ChatMessage(role="user", content="test")
    assert msg.role == "user"
    assert msg.content == "test"


def test_new_chat_request():
    req = NewChatRequest(session_name="Test Session")
    assert req.session_name == "Test Session"


def test_chat_response():
    resp = ChatResponse(
        message_id="123",
        content="test response",
        timestamp="2024-01-01T00:00:00",
        session_id="456"
    )
    assert resp.content == "test response"
    assert resp.session_id == "456"
