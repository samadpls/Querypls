import streamlit as st
from langchain import PromptTemplate, LLMChain, HuggingFaceHub
from deta import Deta
from auth import *


DETA_PROJECT_KEY = "d0spnkqtx1x_6hWnMaUCaEjJ318NHJYy66xrwBqZHKi6"
HUGGINGFACE_API_TOKEN = "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"
REPO_ID = "tiiuae/falcon-7b-instruct"
session = {"key": None}


def configure_page_styles():
    st.set_page_config(page_title="Querypls")
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    hide_streamlit_style = (
        """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
    )
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def display_logo_and_heading():
    img, heading = st.columns([1, 8])
    with img:
        st.image("logo/logo.png", width=40)  # logo
    with heading:
        st.title("Querypls - prompt-2-SQL")  # heading


def handle_new_chat(db):
    database(db)
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How may I help you?"}
    ]


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


def display_user_info():
    st.success("Google Login credentials already provided!", icon="✅")
    st.write("User ID:", st.session_state.user_id)
    st.write("User Email:", st.session_state.user_email)


def display_previous_chats(db):
    previous_chats = db.fetch({"email": st.session_state.user_email})
    for chat in previous_chats.items:
        chat_button = st.button(chat["title"])
        if chat_button:
            st.session_state["messages"] = chat["chat"]
            session["key"] = chat["key"]
            database(db)


def database(db):
    try:
        existing_chat = db.get(key=session["key"])
    except:
        existing_chat = False
    if existing_chat:
        existing_chat["chat"].extend(st.session_state["messages"])
        db.put(existing_chat)
    elif len(st.session_state["messages"]) > 1:
        title = st.session_state["messages"][1]["content"]
        db.put(
            {
                "email": st.session_state.user_email,
                "chat": st.session_state["messages"],
                "title": title[:15] + "....." if len(title) > 15 else title,
            }
        )


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
        display_logo_and_heading()

        if st.button("➕ New chat"):
            handle_new_chat(db)

        if not st.session_state.google_login_run:
            handle_google_login(code)

        if st.session_state.google_login_run:
            display_user_info()
            display_previous_chats(db)

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How may I help you?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    if prompt := st.chat_input(disabled=(code is None)):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        template = """Your task is to create sql query of the following {question}, just sql query and no text
        """
        prompting = PromptTemplate(template=template, input_variables=["question"])
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

