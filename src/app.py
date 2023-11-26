from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import streamlit as st
from deta import Deta
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth import *
from src.constant import *


session = {"key": None}


def configure_page_styles():
    st.set_page_config(page_title="Querypls", page_icon="💬")
    with open("static/css/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    hide_streamlit_style = (
        """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
    )
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def display_logo_and_heading():
    st.image("static/image/logo.png")




def handle_google_login(code):
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


def display_previous_chats(db, max_chat_histories=5):
    previous_chats = db.fetch({"email": st.session_state.user_email}).items
    reversed_chats = reversed(previous_chats)

    for _, chat in enumerate(reversed_chats):
        chat_button = st.button(chat["title"], key=chat["key"])
        if chat_button:
            st.session_state["messages"] = chat["chat"]
            session["key"] = chat["key"]
            database(db)


def database(db, max_chat_histories=5):
    user_email = st.session_state.user_email
    user_chats = db.fetch({"email": user_email}).items
    existing_chat = {"chat": False}

    for chat in user_chats:
        if chat["key"] == session["key"]:
            existing_chat["chat"] = chat["chat"]

    if existing_chat["chat"]:
        new_messages = [
            message
            for message in st.session_state["messages"]
            if message not in existing_chat["chat"]
        ]
        existing_chat["chat"].extend(new_messages)
        db.put(existing_chat)
    elif len(st.session_state["messages"]) > 1:
        title = st.session_state["messages"][1]["content"]
        db.put(
            {
                "email": user_email,
                "chat": st.session_state["messages"],
                "title": title[:25] + "....." if len(title) > 25 else title,
            }
        )

        if len(user_chats) >= max_chat_histories:
            print(user_chats[0]["key"], "user_chats[0]['key']")
            db.delete(user_chats[0]["key"])
            st.warning(
                f"Chat '{user_chats[0]['title']}' has been removed as you reached the limit of {max_chat_histories} chat histories."
            )


def handle_new_chat(db, max_chat_histories=5):
    remaining_chats = max_chat_histories - len(
        db.fetch({"email": st.session_state.user_email}).items
    )
    st.markdown(f" #### Remaining Chats: `{remaining_chats}/{max_chat_histories}`")
    if st.button("➕ New chat"):
        database(db)
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How may I help you?"}
        ]



def main():
    configure_page_styles()
    deta = Deta(DETA_PROJECT_KEY)
    llm = HuggingFaceHub(
        huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        repo_id=REPO_ID,
        model_kwargs={"temperature": 0.2, "max_new_tokens": 180},
    )
    db = deta.Base("users")
    code = st.experimental_get_query_params().get("code", None)

    st.markdown(
        """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>""",
        unsafe_allow_html=True,
    )

    if "google_login_run" not in st.session_state:
        st.session_state.google_login_run = False

    with st.sidebar:
        st.markdown(
            """<a href='https://github.com/samadpls/Querypls'><img src='https://img.shields.io/github/stars/samadpls/querypls?color=red&label=star%20me&logoColor=red&style=social'></a>""",
            unsafe_allow_html=True,
        )

        display_logo_and_heading()
        st.markdown("`Made with 🤍 by samadpls`")

        if not st.session_state.google_login_run:
            handle_google_login(code)
        
        if code is not None:
            handle_new_chat(db)

        if st.session_state.google_login_run:
            display_previous_chats(db)

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How may I help you?"}
        ]
    no_chat_history = len(st.session_state.messages) == 1
    if no_chat_history:
        if "user_email" in st.session_state:
            st.markdown(
                f"""#### Welcome `{st.session_state.user_email}` to \n ## 🛢💬Querypls - Prompt to SQL"""
            )
        else:
            st.markdown(f"#### Welcome to \n ## 🛢💬Querypls - Prompt to SQL")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

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


if __name__ == "__main__":
    main()
