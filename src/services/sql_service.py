import json
import uuid
from datetime import datetime
from typing import Optional
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from src.config.settings import get_settings
from src.schemas.requests import SQLGenerationRequest, ChatMessage
from src.schemas.responses import SQLQueryResponse, ChatResponse, ErrorResponse
from utils.prompt import SQL_GENERATION_PROMPT


class SQLGenerationService:
    def __init__(self, api_key: Optional[str] = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.groq_api_key

        if not self.api_key:
            raise ValueError(
                "Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter."
            )

        self.model = GroqModel(
            self.settings.groq_model_name, provider=GroqProvider(api_key=self.api_key)
        )

        self.agent = Agent(
            self.model, instructions=SQL_GENERATION_PROMPT, output_type=SQLQueryResponse
        )

    def format_chat_history(self, messages: list) -> str:
        history = []
        for msg in messages[1:]:
            if isinstance(msg, ChatMessage):
                content = msg.content
                role = msg.role
            else:
                content = msg.get("content", "")
                role = msg.get("role", "user")

            if "```sql" in content:
                content = content.replace("```sql\n", "").replace("\n```", "").strip()

            history.append(
                {"role": role, "query" if role == "user" else "response": content}
            )

        return json.dumps(history, indent=2)

    def generate_sql(self, request: SQLGenerationRequest) -> ChatResponse:
        try:
            formatted_history = self.format_chat_history(request.conversation_history)
            prompt = f"Previous conversation: {formatted_history}\nCurrent question: {request.user_query}"

            result = self.agent.run_sync(prompt)

            sql_response = SQLQueryResponse(
                sql_query=result.output.sql_query,
                explanation=result.output.explanation,
                tables_used=result.output.tables_used,
                columns_selected=result.output.columns_selected,
                query_type=result.output.query_type,
                complexity=result.output.complexity,
                estimated_rows=result.output.estimated_rows,
                execution_time=result.output.execution_time,
                warnings=result.output.warnings,
            )

            formatted_content = f"```sql\n{sql_response.sql_query}\n```\n\n**Explanation:** {sql_response.explanation}"

            session_id = "default"
            if request.conversation_history:
                first_msg = request.conversation_history[0]
                if isinstance(first_msg, ChatMessage):
                    session_id = first_msg.session_id or "default"
                else:
                    session_id = first_msg.get("session_id", "default")

            chat_response = ChatResponse(
                message_id=str(uuid.uuid4()),
                content=formatted_content,
                sql_response=sql_response,
                timestamp=datetime.now().isoformat(),
                session_id=session_id,
            )

            return chat_response

        except Exception as e:
            error_response = ErrorResponse(
                error_code="SQL_GENERATION_ERROR",
                error_message=f"Error generating SQL: {str(e)}",
                details=str(e),
                timestamp=datetime.now().isoformat(),
            )

            session_id = "default"
            if request.conversation_history:
                first_msg = request.conversation_history[0]
                if isinstance(first_msg, ChatMessage):
                    session_id = first_msg.session_id or "default"
                else:
                    session_id = first_msg.get("session_id", "default")

            return ChatResponse(
                message_id=str(uuid.uuid4()),
                content=f"❌ Error: {error_response.error_message}",
                timestamp=datetime.now().isoformat(),
                session_id=session_id,
            )

    def generate_sql_legacy(self, user_query: str, conversation_history: list) -> str:
        request = SQLGenerationRequest(
            user_query=user_query, conversation_history=conversation_history
        )

        response = self.generate_sql(request)
        return response.content
