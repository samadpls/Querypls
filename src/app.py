from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import streamlit as st
from deta import Deta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth import *
from src.constant import *


def configure_page_styles():
    """Configures Streamlit page styles for Querypls.

    Sets page title, icon, and applies custom CSS styles.
    Hides Streamlit main menu and footer for a cleaner interface.

    Note:
    Ensure 'static/css/styles.css' exists with desired styles.
    """
    st.set_page_config(page_title="Querypls", page_icon="💬")
    with open("static/css/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    hide_streamlit_style = (
        """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
    )
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def display_logo_and_heading():
    """Displays the Querypls logo."""
    st.image("static/image/logo.png")


def handle_google_login(code):
    """Handles Google login authentication.

    Args:
        code (str): Authorization code received from Google.

    Returns:
        None
    """
    if code:
        client = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
        token = asyncio.run(get_access_token(client, REDIRECT_URI, code))
        user_id, user_email = asyncio.run(get_email(client, token["access_token"]))
        if ["user_id", "user_email"] not in st.session_state:
            st.session_state.user_id = user_id
            st.session_state.user_email = user_email
        st.session_state.google_login_run = True
    else:
        st.write(get_login_str(), unsafe_allow_html=True)
    return


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


def initialize_google_login():
    """Initializes the Google login session state."""
    if "google_login_run" not in st.session_state:
        st.session_state.google_login_run = False


def display_github_badge():
    """Displays a GitHub badge with a link to the Querypls repository."""
    st.markdown(
        """<a href='https://github.com/samadpls/Querypls'><img src='https://img.shields.io/github/stars/samadpls/querypls?color=red&label=star%20me&logoColor=red&style=social'></a>""",
        unsafe_allow_html=True,
    )


def handle_google_login_if_needed(code):
    """Handles Google login if it has not been run yet.

    Args:
        code (str): Authorization code received from Google.

    Returns:
        None
    """
    if not st.session_state.google_login_run:
        try:
            handle_google_login(code)
        except:
            st.warning(
                "Seems like there is a network issue. Please check your internet connection."
            )
            sys.exit()


def display_welcome_message():
    """Displays a welcome message based on user chat history."""
    no_chat_history = len(st.session_state.messages) == 1
    if no_chat_history:
        if "user_email" in st.session_state:
            st.markdown(
                f"""#### Welcome `{st.session_state.user_email}` to \n ## 🛢💬Querypls - Prompt to SQL"""
            )
        else:
            st.markdown(f"#### Welcome to \n ## 🛢💬Querypls - Prompt to SQL")
            
def handle_user_input_and_generate_response(code, llm):
    """Handles user input and generates responses using the specified language model.

    Args:
        code (str): Authorization code received from Google.
        llm: Instance of the language model.

    Returns:
        None
    """
    if prompt := st.chat_input(disabled=(code is None)):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        prompting = PromptTemplate(template=TEMPLATE, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompting, llm=llm)

        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Generating..."):
                    response = llm_chain.run(prompt)
                    st.markdown(response, unsafe_allow_html=True)
                    message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(message)


def main():
    """Main function to configure and run the Querypls application."""
    configure_page_styles()
    deta = Deta(DETA_PROJECT_KEY)
    llm = create_huggingface_hub()
    db = deta.Base("users")
    code = st.experimental_get_query_params().get("code", None)

    hide_main_menu_and_footer()
    initialize_google_login()

    with st.sidebar:
        display_github_badge()
        display_logo_and_heading()
        st.markdown("`Made with 🤍 by samadpls`")
        handle_google_login_if_needed(code)
        if code is not None:
            handle_new_chat(db)
        if st.session_state.google_login_run:
            display_previous_chats(db)

    if "messages" not in st.session_state:
        create_message()
    display_welcome_message()

    handle_user_input_and_generate_response(code, llm)


if __name__ == "__main__":
    main()
