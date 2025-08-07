"""
Request schemas for Querypls application.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema for chat message."""
    
    role: Literal["user", "assistant", "system"] = Field(
        description="Message role (user, assistant, system)"
    )
    content: str = Field(
        description="Message content",
        min_length=1
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="Message timestamp"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session identifier"
    )


class SQLGenerationRequest(BaseModel):
    """Schema for SQL generation request."""
    
    user_query: str = Field(
        description="User's natural language query for SQL generation",
        min_length=1,
        max_length=1000
    )
    conversation_history: List[ChatMessage] = Field(
        default=[],
        description="Previous conversation messages for context"
    )
    database_schema: Optional[str] = Field(
        default=None,
        description="Database schema information (optional)"
    )
    query_type: Optional[str] = Field(
        default=None,
        description="Preferred query type (SELECT, INSERT, UPDATE, DELETE)"
    )


class ConversationHistory(BaseModel):
    """Schema for conversation history."""
    
    messages: List[ChatMessage] = Field(
        default=[],
        description="List of conversation messages"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session identifier"
    )


class NewChatRequest(BaseModel):
    """Schema for creating a new chat session."""
    
    session_name: Optional[str] = Field(
        default=None,
        description="Name for the new chat session"
    )
    initial_context: Optional[str] = Field(
        default=None,
        description="Initial context or instructions"
    ) 