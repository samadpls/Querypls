import pytest
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.schemas.requests import ChatMessage, NewChatRequest
from src.schemas.responses import SessionInfo, ChatResponse
from src.backend.orchestrator import BackendOrchestrator


def test_create_new_session():
    orchestrator = BackendOrchestrator()
    session_info = orchestrator.create_new_session(NewChatRequest(session_name="Test Chat"))
    assert session_info.session_name == "Test Chat"
    assert session_info.session_id is not None


def test_list_sessions():
    orchestrator = BackendOrchestrator()
    session1 = orchestrator.create_new_session(NewChatRequest(session_name="Chat 1"))
    session2 = orchestrator.create_new_session(NewChatRequest(session_name="Chat 2"))
    sessions = orchestrator.list_sessions()
    assert len(sessions) == 2
    assert any(s.session_name == "Chat 1" for s in sessions)
    assert any(s.session_name == "Chat 2" for s in sessions)




def test_health_check():
    orchestrator = BackendOrchestrator()
    health = orchestrator.health_check()
    assert health.status in ["healthy", "unhealthy"]
    assert isinstance(health.version, str)
    assert isinstance(health.timestamp, str)


def test_session_message_flow():
    orchestrator = BackendOrchestrator()
    session_info = orchestrator.create_new_session(NewChatRequest(session_name="Test Session"))
    assert session_info.session_name == "Test Session"
    assert session_info.session_id is not None
