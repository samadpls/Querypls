import streamlit as st

def display_logo_and_heading():
    """Displays the Querypls logo."""
    st.image("static/image/logo.png")


def display_welcome_message():
    """Displays a welcome message based on user chat history."""
    no_chat_history = len(st.session_state.messages) == 1
    if no_chat_history:
        st.markdown(f"#### Welcome to \n ## 🗃️💬Querypls - Prompt to SQL")


def handle_new_chat(max_chat_histories=5):
    """Handles the initiation of a new chat session.

    Displays the remaining chat history count and provides a button to start a new chat.

    Args:
        max_chat_histories (int, optional): Maximum number of chat histories to retain.

    Returns:
        None
    """
    remaining_chats = max_chat_histories - len(st.session_state.get("previous_chats", []))
    st.markdown(
        f" #### Remaining Chat Histories: `{remaining_chats}/{max_chat_histories}`"
    )
    st.markdown(
        "You can create up to 5 chat histories. Each history can contain unlimited messages."
    )

    if st.button("➕ New chat"):
        save_chat_history()  # Save current chat before creating a new one
        create_message()


def display_previous_chats():
    """Displays previous chat records stored in session state.

    Allows the user to select a chat to view.
    """
    if "previous_chats" in st.session_state:
        reversed_chats = reversed(st.session_state["previous_chats"])

        for chat in reversed_chats:
            if st.button(chat["title"], key=chat["key"]):
                update_session_state(chat)


def create_message():
    """Creates a default assistant message and initializes a session key."""
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How may I help you?"}
    ]
    st.session_state["key"] = "key"


def update_session_state(chat):
    """Updates the session state with selected chat information.

    Args:
        chat (dict): Selected chat information.
    """
    st.session_state["messages"] = chat["chat"]
    st.session_state["key"] = chat["key"]


def save_chat_history():
    """Saves the current chat to session state if it contains messages."""
    if "messages" in st.session_state and len(st.session_state["messages"]) > 1:
        # Initialize previous chats list if it doesn't exist
        if "previous_chats" not in st.session_state:
            st.session_state["previous_chats"] = []

        # Create a chat summary to store in session
        title = st.session_state["messages"][1]["content"]
        chat_summary = {
            "title": title[:25] + "....." if len(title) > 25 else title,
            "chat": st.session_state["messages"],
            "key": f"chat_{len(st.session_state['previous_chats']) + 1}"
        }

        st.session_state["previous_chats"].append(chat_summary)

        # Limit chat histories to a maximum number
        if len(st.session_state["previous_chats"]) > 5:
            st.session_state["previous_chats"].pop(0)  # Remove oldest chat
            st.warning(
                f"The oldest chat history has been removed as you reached the limit of 5 chat histories."
            )