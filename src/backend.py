import streamlit as st
from streamlit_oauth import OAuth2Component
import sys
import os
import json
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth import *
from src.constant import *

def configure_page_styles(file_name):
    """Configures Streamlit page styles for Querypls.

    Sets page title, icon, and applies custom CSS styles.
    Hides Streamlit main menu and footer for a cleaner interface.

    Note:
    Ensure 'static/css/styles.css' exists with desired styles.
    """
    st.set_page_config(page_title="Querypls", page_icon="💬",layout="wide",)
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

    hide_streamlit_style = (
        """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
    )
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def hide_main_menu_and_footer():
    """Hides the Streamlit main menu and footer for a cleaner interface."""
    st.markdown(
        """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>""",
        unsafe_allow_html=True,
    )
    
def handle_google_login_if_needed(result):
    """Handles Google login if it has not been run yet.

    Args:
        result (str): Authorization code received from Google.

    Returns:
        None
    """
    try:
        if result and "token" in result:
            st.session_state.token = result.get("token")
            token = st.session_state["token"]
            id_token = token["id_token"]
            payload = id_token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            payload = json.loads(base64.b64decode(payload))
            email = payload["email"]
            st.session_state.user_email = email
            st.session_state.code = True
        return
    except:
        st.warning(
            "Seems like there is a network issue. Please check your internet connection."
        )
        sys.exit()
        
def display_github_badge():
    """Displays a GitHub badge with a link to the Querypls repository."""
    st.markdown(
        """<a href='https://github.com/samadpls/Querypls'><img src='https://img.shields.io/github/stars/samadpls/querypls?color=red&label=star%20me&logoColor=red&style=social'></a>""",
        unsafe_allow_html=True,
    )
    

def create_oauth2_component():
    return OAuth2Component(
        CLIENT_ID,
        CLIENT_SECRET,
        AUTHORIZE_URL,
        TOKEN_URL,
        REFRESH_TOKEN_URL,
        REVOKE_TOKEN_URL,
    )

