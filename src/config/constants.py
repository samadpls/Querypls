"""
Constants for Querypls application.
"""

# Application Settings
MAX_RETRIES = 3
EXECUTION_TIMEOUT = 30
MAX_CHAT_HISTORIES = 6
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "localhost"

# Streamlit Configuration
STREAMLIT_CONFIG = {"page_title": "Querypls", "page_icon": "💬", "layout": "wide"}

# Welcome and Session Messages
WELCOME_MESSAGE = "Hello! 👋 I'm Querypls, your SQL and data analysis assistant. I can help you generate SQL queries or analyze CSV files. What would you like to work on today?"
DEFAULT_SESSION_NAME = "Default Chat"

# CSV Analysis Section
CSV_ANALYSIS_SECTION = "### 📊 CSV Analysis"
CSV_UPLOAD_LABEL = "Upload CSV File"
CSV_UPLOAD_HELP = "Upload a CSV file to analyze with Python code"
CSV_PREVIEW = "📋 CSV Preview"
CSV_COLUMNS = "**Columns:** {columns}"
CSV_DTYPES = "**Data Types:** {dtypes}"
LOAD_CSV_BUTTON = "📊 Load CSV Data"
CSV_LOADED_SUCCESS = "✅ CSV data loaded successfully!"
CSV_UPLOAD_SUCCESS = "✅ CSV uploaded successfully! Shape: {shape}"
CSV_UPLOAD_ERROR = "❌ Error uploading CSV: {error}"
CSV_LOAD_ERROR = "❌ No CSV data loaded. Please upload a CSV file first."
CSV_ANALYSIS_ERROR = "❌ Error analyzing CSV: {error}"

# Session Management
SESSION_CREATE_ERROR = "❌ Error creating session: {error}"
SESSION_NOT_FOUND_ERROR = "❌ Session not found"

# worst-case scenario
WORST_CASE_SCENARIO = "I'm here to help! I can assist with SQL generation or CSV data analysis. What would you like to do?"

# Application Errors
ORCHESTRATOR_INIT_ERROR = "❌ Error initializing orchestrator: {error}"
APP_INIT_ERROR = "❌ Error initializing application"
RESPONSE_GENERATION_ERROR = "❌ Error generating response: {error}"
MESSAGE_LOAD_ERROR = "❌ Error loading messages: {error}"
