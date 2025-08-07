"""
Backend orchestrator for managing application state and services.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from config.settings import get_settings
from config.constants import (
    WELCOME_MESSAGE, DEFAULT_SESSION_NAME, CSV_LOAD_ERROR, CSV_ANALYSIS_ERROR,
    SESSION_CREATE_ERROR, ORCHESTRATOR_INIT_ERROR, SESSION_NOT_FOUND_ERROR,
    RESPONSE_GENERATION_ERROR, MESSAGE_LOAD_ERROR, MAX_CHAT_HISTORIES
)
from services.sql_service import SQLGenerationService
from services.csv_analysis_tools import CSVAnalysisTools, create_csv_analysis_agent
from schemas.requests import SQLGenerationRequest, ChatMessage, ConversationHistory, NewChatRequest
from schemas.responses import ChatResponse, SessionInfo, ErrorResponse, HealthCheckResponse


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
        self.sessions: Dict[str, Session] = {}
        self.max_sessions = self.settings.max_chat_histories
    
    def is_conversational_query(self, query: str) -> bool:
        conversational_keywords = [
            'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
            'how are you', 'what\'s up', 'thanks', 'thank you', 'bye', 'goodbye',
            'help', 'what can you do', 'who are you', 'tell me about yourself'
        ]
        query_lower = query.lower().strip()
        return any(keyword in query_lower for keyword in conversational_keywords)
    
    def get_conversational_response(self, query: str) -> str:
        query_lower = query.lower().strip()
        
        if any(greeting in query_lower for greeting in ['hi', 'hello', 'hey']):
            return "Hello! 👋 How can I help you today? I can assist with SQL generation or CSV data analysis."
        elif 'how are you' in query_lower:
            return "I'm doing great, thank you for asking! 😊 How can I assist you with your data queries today?"
        elif any(thanks in query_lower for thanks in ['thanks', 'thank you']):
            return "You're welcome! 😊 Is there anything else I can help you with?"
        elif any(bye in query_lower for bye in ['bye', 'goodbye']):
            return "Goodbye! 👋 Feel free to come back if you need help with SQL or data analysis."
        elif 'help' in query_lower or 'what can you do' in query_lower:
            return "I'm Querypls, your SQL and data analysis assistant! 🗃️💬\n\nI can help you with:\n• **SQL Generation**: Convert natural language to SQL queries\n• **CSV Analysis**: Analyze data files with Python code\n• **Data Visualization**: Create charts and graphs\n\nJust ask me anything about your data!"
        elif 'who are you' in query_lower or 'tell me about yourself' in query_lower:
            return "I'm Querypls, an AI assistant specialized in SQL generation and data analysis! 🗃️💬\n\nI can help you write SQL queries from natural language and analyze CSV files with Python code. What would you like to work on?"
        else:
            return "I'm here to help! I can assist with SQL generation or CSV data analysis. What would you like to do?"
    
    def create_new_session(self, request: NewChatRequest) -> SessionInfo:
        session_id = str(uuid.uuid4())
        session_name = request.session_name or f"Chat {len(self.sessions) + 1}"
        
        messages = []
        if request.initial_context:
            messages.append(ChatMessage(
                role="system",
                content=request.initial_context
            ))
        
        messages.append(ChatMessage(
            role="assistant",
            content=WELCOME_MESSAGE
        ))
        
        session = Session(
            session_id=session_id,
            session_name=session_name,
            created_at=datetime.now(),
            messages=messages,
            last_activity=datetime.now()
        )
        
        self.sessions[session_id] = session
        self._cleanup_old_sessions()
        
        return SessionInfo(
            session_id=session_id,
            session_name=session_name,
            created_at=session.created_at.isoformat(),
            message_count=len(session.messages),
            last_activity=session.last_activity.isoformat()
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
                last_activity=session.last_activity.isoformat()
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
    
    def generate_sql_response(self, session_id: str, user_query: str) -> ChatResponse:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        user_message = ChatMessage(
            role="user",
            content=user_query,
            timestamp=datetime.now().isoformat()
        )
        session.messages.append(user_message)
        
        # Check if this is a conversational query
        if self.is_conversational_query(user_query):
            response_content = self.get_conversational_response(user_query)
        else:
            # Generate SQL for data-related queries
            request = SQLGenerationRequest(
                user_query=user_query,
                conversation_history=session.messages
            )
            
            response = self.sql_service.generate_sql(request)
            response_content = response.content
        
        assistant_message = ChatMessage(
            role="assistant",
            content=response_content,
            timestamp=datetime.now().isoformat()
        )
        session.messages.append(assistant_message)
        session.last_activity = datetime.now()
        
        return ChatResponse(
            message_id=str(uuid.uuid4()),
            content=response_content,
            timestamp=datetime.now().isoformat(),
            session_id=session_id
        )
    
    def generate_csv_analysis_response(self, session_id: str, user_query: str) -> ChatResponse:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if not session.csv_data:
            error_response = ChatResponse(
                message_id=str(uuid.uuid4()),
                content=CSV_LOAD_ERROR,
                timestamp=datetime.now().isoformat(),
                session_id=session_id
            )
            return error_response
        
        user_message = ChatMessage(
            role="user",
            content=user_query,
            timestamp=datetime.now().isoformat()
        )
        session.messages.append(user_message)
        
        try:
            result = self.csv_agent.run_sync(user_query)
            
            assistant_message = ChatMessage(
                role="assistant",
                content=result.output,
                timestamp=datetime.now().isoformat()
            )
            session.messages.append(assistant_message)
            session.last_activity = datetime.now()
            
            return ChatResponse(
                message_id=str(uuid.uuid4()),
                content=result.output,
                timestamp=datetime.now().isoformat(),
                session_id=session_id
            )
            
        except Exception as e:
            error_response = ChatResponse(
                message_id=str(uuid.uuid4()),
                content=CSV_ANALYSIS_ERROR.format(error=str(e)),
                timestamp=datetime.now().isoformat(),
                session_id=session_id
            )
            return error_response
    
    def get_conversation_history(self, session_id: str) -> ConversationHistory:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        return ConversationHistory(
            messages=session.messages,
            session_id=session_id
        )
    
    def get_csv_info(self, session_id: str) -> Dict[str, Any]:
        return self.csv_tools.get_csv_info(session_id)
    
    def health_check(self) -> HealthCheckResponse:
        services_status = {
            "sql_service": "healthy",
            "csv_analysis_service": "healthy",
            "session_manager": "healthy"
        }
        
        try:
            test_request = SQLGenerationRequest(
                user_query="SELECT 1",
                conversation_history=[]
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
        
        return HealthCheckResponse(
            status="healthy" if all(status == "healthy" for status in services_status.values()) else "unhealthy",
            version=self.settings.app_version,
            timestamp=datetime.now().isoformat(),
            services=services_status
        )
    
    def _cleanup_old_sessions(self):
        if len(self.sessions) <= self.max_sessions:
            return
        
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].last_activity
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