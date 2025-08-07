"""
Backend orchestrator for managing application state and services.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from src.config.settings import get_settings
from src.config.constants import WELCOME_MESSAGE, DEFAULT_SESSION_NAME
from src.services.sql_service import SQLGenerationService
from src.services.csv_analysis_tools import CSVAnalysisTools, create_csv_analysis_agent
from src.services.conversation_service import ConversationService
from src.services.routing_service import IntelligentRoutingService
from src.schemas.requests import (
    SQLGenerationRequest,
    ChatMessage,
    ConversationHistory,
    NewChatRequest,
)
from src.schemas.responses import (
    ChatResponse,
    SessionInfo,
    HealthCheckResponse,
)


@dataclass
class Session:
    session_id: str
    session_name: str
    created_at: datetime
    messages: List[ChatMessage]
    last_activity: datetime
    csv_data: Optional[str] = None


class BackendOrchestrator:
    def __init__(self):
        self.settings = get_settings()
        self.sql_service = SQLGenerationService()
        self.csv_tools = CSVAnalysisTools()
        self.csv_agent = create_csv_analysis_agent()
        self.conversation_service = ConversationService()
        self.routing_service = IntelligentRoutingService()
        self.sessions: Dict[str, Session] = {}
        self.max_sessions = self.settings.max_chat_histories

    def create_new_session(self, request: NewChatRequest) -> SessionInfo:
        session_id = str(uuid.uuid4())
        session_name = request.session_name or f"Chat {len(self.sessions) + 1}"

        messages = []
        if request.initial_context:
            messages.append(ChatMessage(
                role="system", content=request.initial_context))

        messages.append(ChatMessage(role="assistant", content=WELCOME_MESSAGE))

        session = Session(
            session_id=session_id,
            session_name=session_name,
            created_at=datetime.now(),
            messages=messages,
            last_activity=datetime.now(),
        )

        self.sessions[session_id] = session
        self._cleanup_old_sessions()

        return SessionInfo(
            session_id=session_id,
            session_name=session_name,
            created_at=session.created_at.isoformat(),
            message_count=len(session.messages),
            last_activity=session.last_activity.isoformat(),
        )

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[SessionInfo]:
        return [
            SessionInfo(
                session_id=session.session_id,
                session_name=session.session_name,
                created_at=session.created_at.isoformat(),
                message_count=len(session.messages),
                last_activity=session.last_activity.isoformat(),
            )
            for session in self.sessions.values()
        ]

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            self.csv_tools.close_session(session_id)
            del self.sessions[session_id]
            return True
        return False

    def load_csv_data(self, session_id: str, csv_content: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.csv_data = csv_content
        result = self.csv_tools.load_csv_data(csv_content, session_id)
        session.last_activity = datetime.now()

        return result

    def generate_intelligent_response(
        self, session_id: str, user_query: str
    ) -> ChatResponse:
        """Generate response using intelligent routing to determine the appropriate agent."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        user_message = ChatMessage(
            role="user", content=user_query, timestamp=datetime.now().isoformat()
        )
        session.messages.append(user_message)

        # Determine which agent should handle this query
        csv_loaded = bool(session.csv_data)
        routing_decision = self.routing_service.determine_agent(
            user_query, session.messages, csv_loaded
        )

        # Generate response based on routing decision
        if routing_decision.agent == "CONVERSATION_AGENT":
            response_content = self.routing_service.handle_conversation_query(
                user_query
            )
        elif routing_decision.agent == "SQL_AGENT":
            response_content = self.routing_service.handle_sql_query(
                user_query, session.messages
            )
        elif routing_decision.agent == "CSV_AGENT":
            if session.csv_data:
                response_content = self.routing_service.handle_csv_query(
                    user_query, session.csv_data, session.messages
                )
            else:
                response_content = "I don't see any CSV data loaded. Please upload a CSV file first to analyze it."
        else:
            # Fallback to conversation
            response_content = self.routing_service.handle_conversation_query(
                user_query
            )

        assistant_message = ChatMessage(
            role="assistant",
            content=response_content,
            timestamp=datetime.now().isoformat(),
        )
        session.messages.append(assistant_message)
        session.last_activity = datetime.now()

        return ChatResponse(
            message_id=str(uuid.uuid4()),
            content=response_content,
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
        )

    def get_conversation_history(self, session_id: str) -> ConversationHistory:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return ConversationHistory(messages=session.messages, session_id=session_id)

    def get_csv_info(self, session_id: str) -> Dict[str, Any]:
        return self.csv_tools.get_csv_info(session_id)

    def health_check(self) -> HealthCheckResponse:
        services_status = {
            "sql_service": "healthy",
            "csv_analysis_service": "healthy",
            "conversation_service": "healthy",
            "session_manager": "healthy",
        }

        try:
            test_request = SQLGenerationRequest(
                user_query="SELECT 1", conversation_history=[]
            )
            if not self.sql_service:
                services_status["sql_service"] = "unhealthy"
        except Exception:
            services_status["sql_service"] = "unhealthy"

        try:
            if not self.csv_tools:
                services_status["csv_analysis_service"] = "unhealthy"
        except Exception:
            services_status["csv_analysis_service"] = "unhealthy"

        try:
            if not self.conversation_service:
                services_status["conversation_service"] = "unhealthy"
        except Exception:
            services_status["conversation_service"] = "unhealthy"

        return HealthCheckResponse(
            status=(
                "healthy"
                if all(status == "healthy" for status in services_status.values())
                else "unhealthy"
            ),
            version=self.settings.app_version,
            timestamp=datetime.now().isoformat(),
            services=services_status,
        )

    def _cleanup_old_sessions(self):
        if len(self.sessions) <= self.max_sessions:
            return

        sorted_sessions = sorted(
            self.sessions.items(), key=lambda x: x[1].last_activity
        )

        sessions_to_remove = len(self.sessions) - self.max_sessions
        for i in range(sessions_to_remove):
            session_id, _ = sorted_sessions[i]
            self.delete_session(session_id)

    def get_default_session(self) -> str:
        for session_id, session in self.sessions.items():
            if session.session_name == DEFAULT_SESSION_NAME:
                return session_id

        request = NewChatRequest(session_name=DEFAULT_SESSION_NAME)
        session_info = self.create_new_session(request)
        return session_info.session_id
