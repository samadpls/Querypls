"""
Application settings with environment variable support.
"""

import os
from typing import Optional, ClassVar
from pydantic import Field, BaseModel, ConfigDict



class Settings(BaseModel):
    groq_api_key: str = Field(default=os.getenv("GROQ_API_KEY", "mock_api_key"), env="GROQ_API_KEY")
    groq_model_name: str = Field(
        default="openai/gpt-oss-120b", env="GROQ_MODEL_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    max_chat_histories: int = Field(default=5, env="MAX_CHAT_HISTORIES")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")

    # Legacy fields for backward compatibility
    max_tokens: Optional[str] = Field(1000, env="MAX_TOKENS")
    temperature: Optional[str] = Field(0.7, env="TEMPERATURE")
    log_level: Optional[str] = Field("INFO", env="LOG_LEVEL")

    json_schema_extra: ClassVar[str] = "ignore"

    model_config = ConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
    )


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance

