"""
Intelligent routing service for determining which agent should handle user queries.
"""

import json
from typing import List, Optional, Dict, Any
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from src.config.constants import WORST_CASE_SCENARIO
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
            context = self._prepare_sql_context(user_query, conversation_history)
            result = self.sql_agent.run_sync(context)

            if hasattr(result.output, "sql_query"):
                return self._format_sql_response(result.output)
            else:
                return "I'm sorry, I couldn't generate a SQL query for that request. Could you please rephrase your question?"

        except Exception as e:
            return f"I encountered an error while generating SQL: {str(e)}"

    def handle_csv_query(
        self,
        user_query: str,
        csv_info: Dict[str, Any],
        conversation_history: Optional[List[ChatMessage]] = None,
    ) -> str:
        """Handle CSV analysis queries."""
        try:
            # Use the AI agent to generate code based on user request and conversation history
            context = self._prepare_csv_context(
                user_query, csv_info, conversation_history
            )
            result = self.csv_agent.run_sync(context)

            if hasattr(result.output, "python_code"):
                # Execute the generated code using Jupyter service
                return self._execute_csv_analysis(
                    result.output.python_code, csv_info, result.output.explanation
                )
            else:
                return "I'm sorry, I couldn't generate analysis code for that request. Could you please rephrase your question?"

        except Exception as e:
            # If LLM fails, provide a graceful response without showing errors
            return WORST_CASE_SCENARIO 

    def _execute_csv_analysis(
        self, python_code: str, csv_info: Dict[str, Any], explanation: str
    ) -> str:
        """Execute CSV analysis code using Jupyter service with error fixing retry loop."""
        try:
            from src.services.jupyter_service import CSVAnalysisService

            # Create Jupyter service instance
            jupyter_service = CSVAnalysisService()

            # Create a temporary session for this analysis
            session_id = "csv_analysis_temp"

            # Load CSV data into the session
            jupyter_service.load_csv_data(session_id, csv_info["file_path"])

            # Install required libraries if needed
            install_code = """
import sys
import subprocess

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages
install_package('pandas')
install_package('numpy')
install_package('matplotlib')
install_package('seaborn')
"""

            # Execute installation first
            install_result = jupyter_service.execute_analysis(
                session_id, install_code, max_retries=1
            )

            # Retry loop for code execution with error fixing
            current_code = python_code
            max_retries = 3

            for attempt in range(max_retries):
                # Execute the current code
                result = jupyter_service.execute_analysis(
                    session_id, current_code, max_retries=1
                )

                if result["status"] == "success":
                    output = result.get("output", "")

                    # If output is empty, provide a fallback
                    if not output.strip():
                        output = "Analysis completed successfully but no output was generated."

                    # Check if any images were created in the specific session directory
                    import os
                    import glob

                    # Look for images in the session's temp directory
                    session_temp_dir = f"/tmp/querypls_session_csv_analysis_temp"
                    image_files = []

                    if os.path.exists(session_temp_dir):
                        png_files = glob.glob(os.path.join(session_temp_dir, "*.png"))
                        jpg_files = glob.glob(os.path.join(session_temp_dir, "*.jpg"))
                        image_files.extend(png_files + jpg_files)

                    if image_files:
                        image_info = "\n\n📊 **Charts generated:**\n"
                        for img_file in image_files:
                            image_info += f"- {os.path.basename(img_file)}\n"
                        output += image_info

                    # Return only the human-readable output, not technical details
                    return output.strip()

                else:
                    # Code execution failed - try to fix it
                    error_msg = result.get("error_message", "Unknown error")

                    if attempt < max_retries - 1:  # Not the last attempt
                        # Send error to LLM to fix the code
                        fixed_code = self._fix_python_code(
                            current_code, error_msg, csv_info
                        )
                        if fixed_code:
                            current_code = fixed_code
                            continue  # Try again with fixed code

                    return WORST_CASE_SCENARIO 

        except Exception as e:
            return WORST_CASE_SCENARIO 

        except Exception as e:
            return WORST_CASE_SCENARIO 

        return WORST_CASE_SCENARIO 

    def _fix_python_code(
        self, original_code: str, error_message: str, csv_info: Dict[str, Any]
    ) -> Optional[str]:
        """Send error to LLM to fix the Python code."""
        try:
            context = self._prepare_code_fix_context(
                original_code, error_message, csv_info
            )

            result = self.csv_agent.run_sync(context)

            if hasattr(result.output, "python_code"):
                return result.output.python_code
            else:
                return None

        except Exception as e:
            return None

    def _prepare_routing_context(
        self, user_query: str, conversation_history: List[ChatMessage], csv_loaded: bool
    ) -> str:
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

    def _prepare_csv_context(
        self,
        user_query: str,
        csv_info: Dict[str, Any],
        conversation_history: Optional[List[ChatMessage]] = None,
    ) -> str:
        """Prepare context for CSV analysis."""
        context_parts = [
            f"User Query: {user_query}",
            f"CSV Data Available: Yes",
            f"CSV File Path: {csv_info['file_path']}",
            f"CSV Shape: {csv_info['shape']}",
            f"CSV Columns: {csv_info['columns']}",
            f"CSV Data Types: {csv_info['dtypes']}",
            f"CSV Sample Data: {csv_info['sample_data']}",
        ]

        if conversation_history:
            context_parts.append("Conversation History:")
            # Last 5 messages for context
            for msg in conversation_history[-5:]:
                context_parts.append(f"- {msg.role}: {msg.content}")

        context_parts.append(
            "\nGenerate SUPER SIMPLE Python code that directly answers the user's question."
        )
        context_parts.append("MAXIMUM 5 LINES OF CODE - Keep it extremely simple!")
        context_parts.append(
            "NO FUNCTIONS OR CLASSES - Just direct code that prints results!"
        )
        context_parts.append(
            f"IMPORTANT: Use pd.read_csv('{csv_info['file_path']}') to load the data from the file path!"
        )
        context_parts.append(
            "Print human-readable results like 'Average price: $123.45' - NO technical output!"
        )
        context_parts.append(
            "For charts, use plt.savefig('/tmp/querypls_session_csv_analysis_temp/chart.png') and plt.show()."
        )

        return "\n".join(context_parts)

    def _prepare_code_fix_context(
        self, original_code: str, error_message: str, csv_info: Dict[str, Any]
    ) -> str:
        """Prepare context for code fixing."""
        context_parts = [
            "CODE FIXING REQUEST:",
            f"Original Code: {original_code}",
            f"Error Message: {error_message}",
            f"CSV File Path: {csv_info['file_path']}",
            f"CSV Shape: {csv_info['shape']}",
            f"CSV Columns: {csv_info['columns']}",
            f"CSV Data Types: {csv_info['dtypes']}",
            f"CSV Sample Data: {csv_info['sample_data']}",
            "",
            "INSTRUCTIONS:",
            "The above Python code failed to execute. Please fix the code and return a working version.",
            "Follow these guidelines:",
            "1. Keep code SIMPLE - Maximum 6 lines",
            "2. NO SPECIAL CHARACTERS - Use standard ASCII only",
            "3. NO FUNCTIONS - Write code directly",
            "4. NO DOCSTRINGS - No complex documentation",
            "5. Use pd.read_csv('file_path') to load data",
            "6. Print human-readable insights directly",
            "7. For charts, save to /tmp/querypls_session_csv_analysis_temp/",
            "",
            "Generate fixed Python code that will execute without errors.",
        ]

        return "\n".join(context_parts)

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
            response_parts.append(f"**Warnings:** {', '.join(sql_response.warnings)}")

        return "\n\n".join(response_parts)

    def _fallback_routing(self, user_query: str, csv_loaded: bool) -> RoutingDecision:
        """Fallback routing when LLM routing fails - let LLM decide, not hardcoded keywords."""
        # Default to conversation - let the LLM handle all decisions
        return RoutingDecision(
            agent="CONVERSATION_AGENT",
            confidence=0.3,
            reasoning="LLM routing failed, defaulting to conversation agent",
        )

    def _get_fallback_conversation_response(self, user_query: str) -> str:
        """Get fallback conversation response when LLM fails."""
        return WORST_CASE_SCENARIO 
