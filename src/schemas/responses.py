"""
Response schemas for Querypls application.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class SQLQueryResponse(BaseModel):
    """Schema for SQL query generation response."""

    sql_query: str = Field(..., description="The generated SQL query as a string")
    explanation: str = Field(
        ..., description="Brief explanation of what the query does"
    )
    tables_used: List[str] = Field(
        default=[], description="Array of table names used in the query"
    )
    columns_selected: List[str] = Field(
        default=[], description="Array of column names selected in the query"
    )
    query_type: Literal[
        "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"
    ] = Field(..., description="Type of query generated")
    complexity: Literal["SIMPLE", "MEDIUM", "COMPLEX"] = Field(
        ..., description="Query complexity level"
    )
    estimated_rows: str = Field(
        default="variable",
        description="Estimated number of rows returned (if applicable)",
    )
    execution_time: Optional[str] = Field(
        default=None, description="Estimated execution time"
    )
    warnings: List[str] = Field(
        default=[], description="Any warnings about the generated query"
    )


class ChatResponse(BaseModel):
    """Schema for chat response."""

    message_id: str = Field(..., description="Unique identifier for the message")
    role: Literal["assistant"] = Field(default="assistant", description="Message role")
    content: str = Field(..., description="Response content")
    sql_response: Optional[SQLQueryResponse] = Field(
        default=None, description="Structured SQL response if applicable"
    )
    timestamp: str = Field(..., description="Response timestamp")
    session_id: str = Field(..., description="Session identifier")


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error_code: str = Field(..., description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(default=None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")


class SessionInfo(BaseModel):
    """Schema for session information."""

    session_id: str = Field(..., description="Unique session identifier")
    session_name: str = Field(..., description="Session name")
    created_at: str = Field(..., description="Session creation timestamp")
    message_count: int = Field(..., description="Number of messages in the session")
    last_activity: str = Field(..., description="Last activity timestamp")


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: Literal["healthy", "unhealthy"] = Field(
        ..., description="Application health status"
    )
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Health check timestamp")
    services: dict = Field(default={}, description="Status of individual services")
