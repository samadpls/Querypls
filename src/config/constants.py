"""
Constants for Querypls application.
"""

# Application Settings
MAX_RETRIES = 3
EXECUTION_TIMEOUT = 30
MAX_CHAT_HISTORIES = 5
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "localhost"

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "page_title": "Querypls",
    "page_icon": "💬",
    "layout": "wide"}

# Available Models
AVAILABLE_MODELS = {
    "deepseek-r1-distill-llama-70b": {
        "developer": "DeepSeek / Meta",
        "context_window": 131072,
        "max_completion": 131072,
        "max_file_size": None,
    },
    "meta-llama/llama-4-maverick-17b-128e-instruct": {
        "developer": "Meta",
        "context_window": 131072,
        "max_completion": 8192,
        "max_file_size": "20 MB",
    },
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "developer": "Meta",
        "context_window": 131072,
        "max_completion": 8192,
        "max_file_size": "20 MB",
    },
    "moonshotai/kimi-k2-instruct": {
        "developer": "Moonshot AI",
        "context_window": 131072,
        "max_completion": 16384,
        "max_file_size": None,
    },
    "openai/gpt-oss-120b": {
        "developer": "OpenAI",
        "context_window": 131072,
        "max_completion": 32766,
        "max_file_size": None,
    },
    "openai/gpt-oss-20b": {
        "developer": "OpenAI",
        "context_window": 131072,
        "max_completion": 32768,
        "max_file_size": None,
    },
    "qwen/qwen3-32b": {
        "developer": "Alibaba Cloud",
        "context_window": 131072,
        "max_completion": 131072,
        "max_file_size": None,
    },
}
