from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import streamlit as st
from streamlit_oauth import OAuth2Component
from deta import Deta
import sys
import time
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


def display_logo_and_heading():
    """Displays the Querypls logo."""
    st.image("static/image/logo.png")


def get_previous_chats(db, user_email):
    """Fetches previous chat records for a user from the database.

    Args:
        db: Deta Base instance.
        user_email (str): User's email address.

    Returns:
        list: List of previous chat records.
    """
    return db.fetch({"email": user_email}).items


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


def database(db, previous_key="key", previous_chat=None, max_chat_histories=5):
    """Manages user chat history in the database.

    Updates, adds, or removes chat history based on user interaction.

    Args:
        db: Deta Base instance.
        previous_key (str): Key for the previous chat in the database.
        previous_chat (list, optional): Previous chat messages.
        max_chat_histories (int, optional): Maximum number of chat histories to retain.

    Returns:
        None
    """
    user_email = st.session_state.user_email
    previous_chats = get_previous_chats(db, user_email)
    existing_chat = db.get(previous_key) if previous_key != "key" else None
    if (
        previous_chat is not None
        and existing_chat is not None
        and previous_key != "key"
    ):
        new_messages = [
            message for message in previous_chat if message not in existing_chat["chat"]
        ]
        existing_chat["chat"].extend(new_messages)
        db.update({"chat": existing_chat["chat"]}, key=previous_key)
        return
    previous_chat = (
        st.session_state.messages if previous_chat is None else previous_chat
    )
    if len(previous_chat) > 1 and previous_key == "key":
        title = previous_chat[1]["content"]
        db.put(
            {
                "email": user_email,
                "chat": previous_chat,
                "title": title[:25] + "....." if len(title) > 25 else title,
            }
        )

        if len(previous_chats) >= max_chat_histories:
            db.delete(previous_chats[0]["key"])
            st.warning(
                f"Chat '{previous_chats[0]['title']}' has been removed as you reached the limit of {max_chat_histories} chat histories."
            )


def create_message():
    """Creates a default assistant message and initializes a session key."""

    st.session_state["messages"] = [
        {"role": "assistant", "content": "How may I help you?"}
    ]
    st.session_state["key"] = "key"
    return


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


def create_huggingface_hub():
    """Creates an instance of Hugging Face Hub with specified configurations.

    Returns:
        HuggingFaceHub: Instance of Hugging Face Hub.
    """
    return HuggingFaceHub(
        huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        repo_id=REPO_ID,
        model_kwargs={"temperature": 0.2, "max_new_tokens": 180},
    )


def hide_main_menu_and_footer():
    """Hides the Streamlit main menu and footer for a cleaner interface."""
    st.markdown(
        """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>""",
        unsafe_allow_html=True,
    )


def display_github_badge():
    """Displays a GitHub badge with a link to the Querypls repository."""
    st.markdown(
        """<a href='https://github.com/samadpls/Querypls'><img src='https://img.shields.io/github/stars/samadpls/querypls?color=red&label=star%20me&logoColor=red&style=social'></a>""",
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


def display_welcome_message():
    """Displays a welcome message based on user chat history."""
    no_chat_history = len(st.session_state.messages) == 1
    if no_chat_history:
        st.markdown(f"#### Welcome to \n ## 🛢💬Querypls - Prompt to SQL")


def create_oauth2_component():
    return OAuth2Component(
        CLIENT_ID,
        CLIENT_SECRET,
        AUTHORIZE_URL,
        TOKEN_URL,
        REFRESH_TOKEN_URL,
        REVOKE_TOKEN_URL,
    )

def main():
    """Main function to configure and run the Querypls application."""
    configure_page_styles('static/css/styles.css')
    deta = Deta(DETA_PROJECT_KEY)
    if "model" not in st.session_state:
        llm = create_huggingface_hub()
        st.session_state["model"] = llm
    db = deta.Base("users")
    oauth2 = create_oauth2_component()

    if "code" not in st.session_state or not st.session_state.code:
        st.session_state.code = False

    # if "code" not in st.session_state:
    #     st.session_state.code = False

    hide_main_menu_and_footer()
    if st.session_state.code == False:
        col1, col2, col3 = st.columns(3)
        with col1:
            pass
        with col2:
            with st.container():

                display_github_badge()
                display_logo_and_heading()

                st.markdown("`Made with 🤍 by samadpls`")
                if "token" not in st.session_state:
                    result = oauth2.authorize_button(
                        "Connect with Google",
                        REDIRECT_URI,
                        SCOPE,
                        icon="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 48 48'%3E%3Cdefs%3E%3Cpath id='a' d='M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 24s9.8 22 22 22c11 0 21-8 21-22 0-1.3-.2-2.7-.5-4z'/%3E%3C/defs%3E%3CclipPath id='b'%3E%3Cuse xlink:href='%23a' overflow='visible'/%3E%3C/clipPath%3E%3Cpath clip-path='url(%23b)' fill='%23FBBC05' d='M0 37V11l17 13z'/%3E%3Cpath clip-path='url(%23b)' fill='%23EA4335' d='M0 11l17 13 7-6.1L48 14V0H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%2334A853' d='M0 37l30-23 7.9 1L48 0v48H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%234285F4' d='M48 48L17 24l-4-3 35-10z'/%3E%3C/svg%3E",
                        use_container_width=True,
                    )
                    handle_google_login_if_needed(result)
                    st.rerun()
        with col3:
            pass
    else:
        with st.sidebar:
            display_github_badge()
            display_logo_and_heading()
            st.markdown("`Made with 🤍 by samadpls`")
            if st.session_state.code:
                handle_new_chat(db)
            if st.session_state.code:
                display_previous_chats(db)

        if "messages" not in st.session_state:
            create_message()
        display_welcome_message()

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)

        if prompt := st.chat_input(disabled=(st.session_state.code is False)):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            prompting = PromptTemplate(template=TEMPLATE, input_variables=["question"])
            if "model" in st.session_state:
                llm_chain = LLMChain(prompt=prompting, llm=st.session_state.model)

                if st.session_state.messages[-1]["role"] != "assistant":
                    with st.chat_message("assistant"):
                        with st.spinner("Generating..."):
                            response = llm_chain.run(prompt)
                            st.markdown(response, unsafe_allow_html=True)
                            message = {"role": "assistant", "content": response}
                            st.session_state.messages.append(message)


if __name__ == "__main__":
    main()
