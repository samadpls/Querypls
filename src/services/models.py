"""
Data models for the services.
"""

from typing import Literal, Union, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RoutingDecision(BaseModel):
    """Model for routing decisions."""

    agent: Literal["CONVERSATION_AGENT", "SQL_AGENT", "CSV_AGENT"] = Field(
        description="The agent that should handle the query"
    )
    confidence: float = Field(
        description="Confidence level in the routing decision", ge=0.0, le=1.0
    )
    reasoning: str = Field(description="Brief explanation of why this agent was chosen")


class ConversationResponse(BaseModel):
    """Response for conversational queries."""

    message: str = Field(description="Natural response to user query")
    response_type: Literal["greeting", "help", "thanks", "goodbye", "general"] = Field(
        description="Type of response"
    )
    suggest_next: Optional[str] = Field(
        description="Optional suggestion for what they could do next", default=None
    )


class SQLResponse(BaseModel):
    """Response for SQL generation."""

    sql_query: str = Field(description="The generated SQL query")
    explanation: str = Field(description="Brief explanation of what the query does")
    tables_used: List[str] = Field(description="Array of table names used in the query")
    columns_selected: List[str] = Field(
        description="Array of column names selected in the query"
    )
    query_type: str = Field(
        description="Type of query (SELECT, INSERT, UPDATE, DELETE, etc.)"
    )
    complexity: Literal["SIMPLE", "MEDIUM", "COMPLEX"] = Field(
        description="Query complexity level"
    )
    estimated_rows: str = Field(description="Estimated number of rows returned")
    execution_time: Optional[str] = Field(
        description="Estimated execution time", default=None
    )
    warnings: List[str] = Field(
        description="Array of warnings about the query", default_factory=list
    )


class CSVAnalysisResponse(BaseModel):
    """Response for CSV analysis."""

    python_code: str = Field(description="The generated Python code")
    explanation: str = Field(description="Brief explanation of what the code does")
    expected_output: str = Field(description="What output is expected from the code")
    libraries_used: List[str] = Field(description="Array of Python libraries used")


class CodeFixResponse(BaseModel):
    """Response for code fixing."""

    python_code: str = Field(description="The fixed Python code")
    explanation: str = Field(description="Brief explanation of what was fixed")
    expected_output: str = Field(
        description="What output is expected from the fixed code"
    )
    libraries_used: List[str] = Field(description="Array of Python libraries used")


class Failed(BaseModel):
    """Unable to find a satisfactory response."""

    error: str = Field(description="Error message explaining the failure")


# Union types for different response types
ConversationResult = Union[ConversationResponse, Failed]
SQLResult = Union[SQLResponse, Failed]
CSVAnalysisResult = Union[CSVAnalysisResponse, Failed]
CodeFixResult = Union[CodeFixResponse, Failed]
