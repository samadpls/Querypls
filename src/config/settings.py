"""
Application settings with environment variable support.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

from src.config.constants import AVAILABLE_MODELS


class Settings(BaseSettings):
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    groq_model_name: str = Field(
        default="openai/gpt-oss-120b",
        env="GROQ_MODEL_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    max_chat_histories: int = Field(default=5, env="MAX_CHAT_HISTORIES")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")

    # Legacy fields for backward compatibility
    app_name: Optional[str] = Field(None, env="APP_NAME")
    streamlit_port: Optional[str] = Field(None, env="STREAMLIT_PORT")
    streamlit_host: Optional[str] = Field(None, env="STREAMLIT_HOST")
    max_tokens: Optional[str] = Field(None, env="MAX_TOKENS")
    temperature: Optional[str] = Field(None, env="TEMPERATURE")
    log_level: Optional[str] = Field(None, env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def get_available_models():
    return AVAILABLE_MODELS


def get_model_info(model_name: str):
    return AVAILABLE_MODELS.get(model_name, None)
