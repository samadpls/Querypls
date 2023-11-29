from streamlit import secrets

DETA_PROJECT_KEY = secrets["DETA_PROJECT_KEY"]
HUGGINGFACE_API_TOKEN = secrets["HUGGINGFACE_API_TOKEN"]
REPO_ID = secrets["REPO_ID"]
CLIENT_ID = secrets["CLIENT_ID"]
CLIENT_SECRET = secrets["CLIENT_SECRET"]
REDIRECT_URI = secrets["REDIRECT_URI"]
TEMPLATE = secrets["TEMPLATE"]
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REFRESH_TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_TOKEN_URL = "https://oauth2.googleapis.com/revoke"
SCOPE = "email"
