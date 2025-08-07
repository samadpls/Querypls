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
    "layout": "wide"
}

# UI Messages
WELCOME_MESSAGE = "How may I help you? I can help with SQL generation or CSV data analysis."
DEFAULT_SESSION_NAME = "Default Chat"

# Success Messages
CSV_LOAD_SUCCESS = "✅ CSV loaded for analysis!"
CSV_UPLOAD_SUCCESS = "✅ CSV uploaded successfully! Shape: {shape}"
CSV_LOADED_SUCCESS = "✅ CSV loaded for analysis!"
SESSION_CREATED = "✅ Created session: {name} (ID: {id})"
SESSION_SWITCHED = "✅ Switched to session: {name}"

# Error Messages
CSV_LOAD_ERROR = "❌ No CSV data loaded. Please upload a CSV file first."
CSV_ANALYSIS_ERROR = "❌ Error during CSV analysis: {error}"
CSV_UPLOAD_ERROR = "❌ Error reading CSV file: {error}"
SESSION_CREATE_ERROR = "Failed to create new session: {error}"
ORCHESTRATOR_INIT_ERROR = "Failed to initialize backend orchestrator: {error}"
SESSION_NOT_FOUND_ERROR = "Failed to get current session."
APP_INIT_ERROR = "Failed to initialize application. Please check your configuration."
RESPONSE_GENERATION_ERROR = "Error generating response: {error}"
MESSAGE_LOAD_ERROR = "Error loading messages: {error}"
SESSION_NOT_FOUND = "❌ Session {id} not found."
NO_ACTIVE_SESSION = "❌ No active session. Create one first with 'new' command."
NO_SESSION = "❌ No active session."
HEALTH_CHECK_FAILED = "❌ Health check failed: {error}"

# Health Check Messages
HEALTH_CHECK_SUCCESS = "🏥 Health Check:"
HEALTH_STATUS = "Status: {status}"
HEALTH_VERSION = "Version: {version}"
HEALTH_SERVICES = "Services: {services}"

# CLI Messages
CLI_WELCOME = "🚀 Welcome to Querypls CLI!"
CLI_COMMANDS = "Commands: new, list, switch <id>, chat <query>, history, health, quit"
CLI_GOODBYE = "👋 Goodbye!"
CLI_UNKNOWN_COMMAND = "❌ Unknown command. Use: new, list, switch <id>, chat <query>, history, health, quit"
CLI_ERROR = "❌ Error: {error}"

# Response Labels
RESPONSE_GENERATED = "🤖 Response:"
SQL_DETAILS = "📊 SQL Details:"
QUERY_TYPE = "Query Type:"
COMPLEXITY = "Complexity:"
TABLES_USED = "Tables Used:"
COLUMNS = "Columns:"
ESTIMATED_ROWS = "Estimated Rows:"
WARNINGS = "Warnings:"
CONVERSATION_HISTORY = "📜 Conversation History:"

# Session Management
NO_SESSIONS = "📝 No sessions found."
AVAILABLE_SESSIONS = "📝 Available sessions:"
SESSION_INFO = "  {num}. {name}"
SESSION_ID = "     ID: {id}"
SESSION_MESSAGES = "     Messages: {count}"
SESSION_ACTIVITY = "     Last Activity: {activity}"

# CSV Analysis UI
CSV_ANALYSIS_SECTION = "### 📊 CSV Analysis"
CSV_UPLOAD_LABEL = "Upload CSV file for analysis"
CSV_UPLOAD_HELP = "Upload a CSV file to analyze with Python code"
CSV_PREVIEW = "📊 CSV Preview"
CSV_COLUMNS = "**Columns:** {columns}"
CSV_DTYPES = "**Data Types:** {dtypes}"
LOAD_CSV_BUTTON = "🔍 Load CSV for Analysis"

# UI Elements
GITHUB_BADGE = """<a href='https://github.com/samadpls/Querypls'>\
<img src='https://img.shields.io/github/stars/samadpls/querypls\
    ?color=red&label=star%20me&logoColor=red&style=social'\
></a>"""

MADE_WITH_LOVE = "`Made with 🤍`"
SESSIONS_SECTION = "### Sessions"
NEW_SESSION_BUTTON = "➕ New Session"

# CSS Styles
HIDE_MENU_STYLE = """<style>#MainMenu {visibility: hidden;}\
footer {visibility: hidden;}</style>"""

HIDE_MENU_FOOTER_STYLE = """<style>#MainMenu {visibility: hidden;}\
        footer {visibility: hidden;}</style>"""

# Available Models
AVAILABLE_MODELS = {
    "deepseek-r1-distill-llama-70b": {
        "developer": "DeepSeek / Meta",
        "context_window": 131072,
        "max_completion": 131072,
        "max_file_size": None
    },
    "meta-llama/llama-4-maverick-17b-128e-instruct": {
        "developer": "Meta",
        "context_window": 131072,
        "max_completion": 8192,
        "max_file_size": "20 MB"
    },
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "developer": "Meta",
        "context_window": 131072,
        "max_completion": 8192,
        "max_file_size": "20 MB"
    },
    "moonshotai/kimi-k2-instruct": {
        "developer": "Moonshot AI",
        "context_window": 131072,
        "max_completion": 16384,
        "max_file_size": None
    },
    "openai/gpt-oss-120b": {
        "developer": "OpenAI",
        "context_window": 131072,
        "max_completion": 32766,
        "max_file_size": None
    },
    "openai/gpt-oss-20b": {
        "developer": "OpenAI",
        "context_window": 131072,
        "max_completion": 32768,
        "max_file_size": None
    },
    "qwen/qwen3-32b": {
        "developer": "Alibaba Cloud",
        "context_window": 131072,
        "max_completion": 131072,
        "max_file_size": None
    }
} 