"""
Intelligent routing service for determining which agent should handle user queries.
"""

import json
from typing import List, Optional
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from src.config.settings import get_settings
from src.services.models import (
    RoutingDecision,
    ConversationResult,
    SQLResult,
    CSVAnalysisResult,
)
from src.schemas.requests import ChatMessage
from utils.prompt import (
    ROUTING_PROMPT,
    CONVERSATION_PROMPT,
    SQL_GENERATION_PROMPT,
    CSV_ANALYSIS_PROMPT,
)


class IntelligentRoutingService:
    """Service for intelligently routing user queries to appropriate agents."""

    def __init__(self):
        self.settings = get_settings()

        self.model = GroqModel(
            self.settings.groq_model_name,
            provider=GroqProvider(api_key=self.settings.groq_api_key),
        )

        # Create routing agent
        self.routing_agent = Agent[None, RoutingDecision](
            self.model, output_type=RoutingDecision, system_prompt=ROUTING_PROMPT
        )

        # Create conversation agent
        self.conversation_agent = Agent[None, ConversationResult](
            self.model,
            output_type=ConversationResult,
            system_prompt=CONVERSATION_PROMPT,
        )

        # Create SQL agent
        self.sql_agent = Agent[None, SQLResult](
            self.model, output_type=SQLResult, system_prompt=SQL_GENERATION_PROMPT
        )

        # Create CSV analysis agent
        self.csv_agent = Agent[None, CSVAnalysisResult](
            self.model, output_type=CSVAnalysisResult, system_prompt=CSV_ANALYSIS_PROMPT
        )

    def determine_agent(
        self,
        user_query: str,
        conversation_history: List[ChatMessage],
        csv_loaded: bool = False,
    ) -> RoutingDecision:
        """Determine which agent should handle the user query."""
        try:
            # Prepare context for routing
            context = self._prepare_routing_context(
                user_query, conversation_history, csv_loaded
            )

            result = self.routing_agent.run_sync(context)
            return result.output

        except Exception as e:
            # Fallback to simple keyword-based routing
            return self._fallback_routing(user_query, csv_loaded)

    def handle_conversation_query(self, user_query: str) -> str:
        """Handle conversational queries."""
        try:
            result = self.conversation_agent.run_sync(user_query)

            if hasattr(result.output, "message"):
                return result.output.message
            else:
                return self._get_fallback_conversation_response(user_query)

        except Exception as e:
            return self._get_fallback_conversation_response(user_query)

    def handle_sql_query(
        self, user_query: str, conversation_history: List[ChatMessage]
    ) -> str:
        """Handle SQL generation queries."""
        try:
            context = self._prepare_sql_context(
                user_query, conversation_history)
            result = self.sql_agent.run_sync(context)

            if hasattr(result.output, "sql_query"):
                return self._format_sql_response(result.output)
            else:
                return "I'm sorry, I couldn't generate a SQL query for that request. Could you please rephrase your question?"

        except Exception as e:
            return f"I encountered an error while generating SQL: {str(e)}"

    def handle_csv_query(self, user_query: str, csv_data: str) -> str:
        """Handle CSV analysis queries."""
        try:
            context = self._prepare_csv_context(user_query, csv_data)
            result = self.csv_agent.run_sync(context)

            if hasattr(result.output, "python_code"):
                return self._format_csv_response(result.output)
            else:
                return "I'm sorry, I couldn't generate analysis code for that request. Could you please rephrase your question?"

        except Exception as e:
            return (
                f"I encountered an error while generating CSV analysis code: {
                    str(e)}")

    def _prepare_routing_context(
            self,
            user_query: str,
            conversation_history: List[ChatMessage],
            csv_loaded: bool) -> str:
        """Prepare context for routing decision."""
        context_parts = [
            f"User Query: {user_query}",
            f"CSV Data Loaded: {csv_loaded}",
        ]

        if conversation_history:
            # Last 5 messages for context
            recent_messages = conversation_history[-5:]
            context_parts.append("Recent Conversation History:")
            for msg in recent_messages:
                context_parts.append(f"- {msg.role}: {msg.content}")

        return "\n".join(context_parts)

    def _prepare_sql_context(
        self, user_query: str, conversation_history: List[ChatMessage]
    ) -> str:
        """Prepare context for SQL generation."""
        context_parts = [
            f"User Query: {user_query}",
        ]

        if conversation_history:
            context_parts.append("Conversation History:")
            for msg in conversation_history[-10:]:  # Last 10 messages
                context_parts.append(f"- {msg.role}: {msg.content}")

        return "\n".join(context_parts)

    def _prepare_csv_context(self, user_query: str, csv_data: str) -> str:
        """Prepare context for CSV analysis."""
        return f"User Query: {user_query}\n\nCSV Data Available: Yes\n\nGenerate Python code to analyze the CSV data based on the user's request."

    def _format_sql_response(self, sql_response) -> str:
        """Format SQL response for display."""
        response_parts = [
            f"**SQL Query:**\n```sql\n{sql_response.sql_query}\n```",
            f"**Explanation:** {sql_response.explanation}",
            f"**Query Type:** {sql_response.query_type}",
            f"**Complexity:** {sql_response.complexity}",
            f"**Tables Used:** {', '.join(sql_response.tables_used)}",
            f"**Columns Selected:** {', '.join(sql_response.columns_selected)}",
            f"**Estimated Rows:** {sql_response.estimated_rows}",
        ]

        if sql_response.warnings:
            response_parts.append(
                f"**Warnings:** {', '.join(sql_response.warnings)}")

        return "\n\n".join(response_parts)

    def _format_csv_response(self, csv_response) -> str:
        """Format CSV analysis response for display."""
        response_parts = [
            f"**Python Code:**\n```python\n{csv_response.python_code}\n```",
            f"**Explanation:** {csv_response.explanation}",
            f"**Expected Output:** {csv_response.expected_output}",
            f"**Libraries Used:** {', '.join(csv_response.libraries_used)}",
        ]

        return "\n\n".join(response_parts)

    def _fallback_routing(
            self,
            user_query: str,
            csv_loaded: bool) -> RoutingDecision:
        """Fallback routing based on simple keyword matching."""
        query_lower = user_query.lower().strip()

        # Conversation keywords
        conversation_keywords = [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "how are you",
            "what's up",
            "thanks",
            "thank you",
            "bye",
            "goodbye",
            "help",
            "what can you do",
            "who are you",
            "tell me about yourself",
        ]

        # CSV keywords
        csv_keywords = [
            "csv",
            "data",
            "analyze",
            "analysis",
            "chart",
            "graph",
            "plot",
            "visualize",
            "pandas",
            "matplotlib",
            "seaborn",
            "python",
            "code",
            "file",
        ]

        # SQL keywords
        sql_keywords = [
            "select",
            "from",
            "where",
            "join",
            "table",
            "database",
            "query",
            "sql",
            "insert",
            "update",
            "delete",
            "create",
            "alter",
            "drop",
        ]

        if any(keyword in query_lower for keyword in conversation_keywords):
            return RoutingDecision(
                agent="CONVERSATION_AGENT",
                confidence=0.8,
                reasoning="Detected conversational keywords",
            )
        elif csv_loaded and any(keyword in query_lower for keyword in csv_keywords):
            return RoutingDecision(
                agent="CSV_AGENT",
                confidence=0.7,
                reasoning="CSV data loaded and detected CSV-related keywords",
            )
        elif any(keyword in query_lower for keyword in sql_keywords):
            return RoutingDecision(
                agent="SQL_AGENT",
                confidence=0.7,
                reasoning="Detected SQL-related keywords",
            )
        else:
            # Default to conversation for unknown queries
            return RoutingDecision(
                agent="CONVERSATION_AGENT",
                confidence=0.5,
                reasoning="No specific keywords detected, defaulting to conversation",
            )

    def _get_fallback_conversation_response(self, user_query: str) -> str:
        """Get fallback conversation response. Wish it dont be here."""
        query_lower = user_query.lower().strip()

        if any(greeting in query_lower for greeting in ["hi", "hello", "hey"]):
            return "Hello! 👋 I'm Querypls, your SQL and data analysis assistant. I can help you generate SQL queries or analyze CSV files. What would you like to work on today?"
        elif "how are you" in query_lower:
            return "I'm doing great, thank you for asking! 😊 I'm ready to help you with SQL queries or CSV data analysis. What can I assist you with?"
        elif any(thanks in query_lower for thanks in ["thanks", "thank you"]):
            return "You're welcome! 😊 Is there anything else I can help you with?"
        elif any(bye in query_lower for bye in ["bye", "goodbye"]):
            return "Goodbye! 👋 Feel free to come back if you need help with SQL or data analysis."
        elif "help" in query_lower or "what can you do" in query_lower:
            return "I'm Querypls, your data analysis companion! 🗃️💬 I can help you with SQL generation and CSV data analysis. Just upload a CSV file or ask me to write SQL queries!"
        else:
            return "I'm here to help! I can assist with SQL generation or CSV data analysis. What would you like to do?"
