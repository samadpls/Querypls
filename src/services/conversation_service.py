"""
Conversation service for handling normal user queries.
"""

from typing import Literal, Union
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from src.config.settings import get_settings
from src.services.models import ConversationResponse, Failed
from utils.prompt import CONVERSATION_PROMPT


class ConversationService:
    def __init__(self):
        self.settings = get_settings()

        self.model = GroqModel(
            self.settings.groq_model_name,
            provider=GroqProvider(api_key=self.settings.groq_api_key),
        )

        self.conversation_agent = Agent[None, Union[ConversationResponse, Failed]](
            self.model,
            output_type=Union[ConversationResponse, Failed],
            system_prompt=CONVERSATION_PROMPT,
        )

    def is_conversational_query(self, query: str) -> bool:
        """Check if query is conversational (not SQL/data related)."""
        conversational_keywords = [
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
            "nice to meet you",
            "pleasure",
            "good",
            "fine",
            "okay",
        ]
        query_lower = query.lower().strip()
        return any(keyword in query_lower for keyword in conversational_keywords)

    def get_conversational_response(self, query: str) -> str:
        """Get a natural response for conversational queries."""
        try:
            result = self.conversation_agent.run_sync(query)

            if isinstance(result.output, ConversationResponse):
                return result.output.message
            else:
                # Fallback responses
                query_lower = query.lower().strip()

                if any(greeting in query_lower for greeting in ["hi", "hello", "hey"]):
                    return "Hello! 👋 How can I help you today? I can assist with SQL generation or CSV data analysis."
                elif "how are you" in query_lower:
                    return "I'm doing great, thank you for asking! 😊 How can I assist you with your data queries today?"
                elif any(thanks in query_lower for thanks in ["thanks", "thank you"]):
                    return (
                        "You're welcome! 😊 Is there anything else I can help you with?"
                    )
                elif any(bye in query_lower for bye in ["bye", "goodbye"]):
                    return "Goodbye! 👋 Feel free to come back if you need help with SQL or data analysis."
                elif "help" in query_lower or "what can you do" in query_lower:
                    return "I'm Querypls, your SQL and data analysis assistant! 🗃️💬\n\nI can help you with:\n• **SQL Generation**: Convert natural language to SQL queries\n• **CSV Analysis**: Analyze data files with Python code\n• **Data Visualization**: Create charts and graphs\n\nJust ask me anything about your data!"
                else:
                    return "I'm here to help! I can assist with SQL generation or CSV data analysis. What would you like to do?"

        except Exception as e:
            # Fallback response
            return "Hello! How can I help you today? I can assist with SQL generation or CSV data analysis."
