"""
Frontend utilities for Streamlit interface components.
"""

import streamlit as st


def display_logo_and_heading():
    st.image("static/image/logo.png")


def display_welcome_message():
    st.markdown("#### Welcome to \n ## 🗃️💬Querypls - Prompt to SQL")


def handle_new_chat(max_chat_histories=5):
    st.markdown(f"#### Remaining Chat Histories: `{max_chat_histories}`")
    st.markdown(
        "You can create multiple chat sessions. Each session can contain unlimited messages."
    )

    if st.button("➕ New chat"):
        st.rerun()


def display_previous_chats():
    pass


def create_message():
    pass


def update_session_state(chat):
    pass


def save_chat_history():
    pass
