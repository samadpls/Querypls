import streamlit as st
from src.database import database, get_previous_chats

def display_logo_and_heading():
    """Displays the Querypls logo."""
    st.image("static/image/logo.png")

def display_welcome_message():
    """Displays a welcome message based on user chat history."""
    no_chat_history = len(st.session_state.messages) == 1
    if no_chat_history:
        st.markdown(f"#### Welcome to \n ## 🛢💬Querypls - Prompt to SQL")
        
def handle_new_chat(db, max_chat_histories=5):
    """Handles the initiation of a new chat session.

    Displays the remaining chat history count and provides a button to start a new chat.

    Args:
        db: Deta Base instance.
        max_chat_histories (int, optional): Maximum number of chat histories to retain.

    Returns:
        None
    """
    remaining_chats = max_chat_histories - len(
        get_previous_chats(db, st.session_state.user_email)
    )
    st.markdown(f" #### Remaining Chats: `{remaining_chats}/{max_chat_histories}`")
    if st.button("➕ New chat"):
        database(db, previous_key=st.session_state.key)
        create_message()
        
def display_previous_chats(db):
    """Displays previous chat records.

    Retrieves and displays a list of previous chat records for the user.
    Allows the user to select a chat to view.

    Args:
        db: Deta Base instance.

    Returns:
        None
    """
    previous_chats = get_previous_chats(db, st.session_state.user_email)
    reversed_chats = reversed(previous_chats)

    for chat in reversed_chats:
        if st.button(chat["title"], key=chat["key"]):
            update_session_state(db, chat)
            
def create_message():
    """Creates a default assistant message and initializes a session key."""

    st.session_state["messages"] = [
        {"role": "assistant", "content": "How may I help you?"}
    ]
    st.session_state["key"] = "key"
    return

def update_session_state(db, chat):
    """Updates the session state with selected chat information.

    Args:
        db: Deta Base instance.
        chat (dict): Selected chat information.

    Returns:
        None
    """
    previous_chat = st.session_state["messages"]
    previous_key = st.session_state["key"]
    st.session_state["messages"] = chat["chat"]
    st.session_state["key"] = chat["key"]
    database(db, previous_key, previous_chat)


