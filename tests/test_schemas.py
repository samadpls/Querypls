import pytest
import json
from src.schemas.requests import (
    SQLGenerationRequest,
    ChatMessage,
    ConversationHistory,
    NewChatRequest,
)
from src.schemas.responses import (
    SQLQueryResponse,
    ChatResponse,
    ErrorResponse,
    SessionInfo,
    HealthCheckResponse,
)


def test_sql_generation_request():
    request = SQLGenerationRequest(
        user_query="Show users",
        conversation_history=[],
        database_schema=None,
        query_type=None,
    )
    assert request.user_query == "Show users"
    assert isinstance(request.conversation_history, list)


def test_chat_message():
    message = ChatMessage(
        role="user", content="Hello", timestamp="2024-01-01T00:00:00", session_id="123"
    )
    assert message.role == "user"
    assert message.content == "Hello"
    assert message.timestamp == "2024-01-01T00:00:00"
    assert message.session_id == "123"


def test_conversation_history():
    history = ConversationHistory(
        messages=[ChatMessage(role="user", content="Hello")], session_id="123"
    )
    assert len(history.messages) == 1
    assert history.session_id == "123"


def test_new_chat_request():
    request = NewChatRequest(session_name="Test Chat", initial_context="SQL Testing")
    assert request.session_name == "Test Chat"
    assert request.initial_context == "SQL Testing"


def test_sql_query_response():
    response = SQLQueryResponse(
        sql_query="SELECT * FROM users",
        explanation="Get all users",
        tables_used=["users"],
        columns_selected=["*"],
        query_type="SELECT",
        complexity="SIMPLE",
    )
    assert response.sql_query == "SELECT * FROM users"
    assert response.explanation == "Get all users"
    assert response.tables_used == ["users"]


def test_chat_response():
    response = ChatResponse(
        message_id="123",
        content="Hello",
        timestamp="2024-01-01T00:00:00",
        session_id="456",
    )
    assert response.message_id == "123"
    assert response.content == "Hello"
    assert response.session_id == "456"


def test_health_check_response():
    response = HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        timestamp="2024-01-01T00:00:00",
        services={"sql": "healthy"},
    )
    assert response.status == "healthy"
    assert response.version == "1.0.0"
    assert response.services["sql"] == "healthy"
