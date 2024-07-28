from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import streamlit as st
from deta import Deta
import sys
import os
from backend import (
    configure_page_styles,
    create_oauth2_component,
    display_github_badge,
    handle_google_login_if_needed,
    hide_main_menu_and_footer,
)
from frontend import (
    create_message,
    display_logo_and_heading,
    display_previous_chats,
    display_welcome_message,
    handle_new_chat,
)
from model import create_huggingface_hub


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth import *
from src.constant import *


def main():
    """Main function to configure and run the Querypls application."""
    configure_page_styles("static/css/styles.css")
    deta = Deta(DETA_PROJECT_KEY)
    if "model" not in st.session_state:
        llm = create_huggingface_hub()
        st.session_state["model"] = llm
    db = deta.Base("users")
    oauth2 = create_oauth2_component()

    if "code" not in st.session_state or not st.session_state.code:
        st.session_state.code = False

    if "code" not in st.session_state:
        st.session_state.code = False

    hide_main_menu_and_footer()
    if st.session_state.code == False:
        col1, col2, col3 = st.columns(3)
        with col1:
            pass
        with col2:
            with st.container():

                display_github_badge()
                display_logo_and_heading()

                st.markdown("`Made with 🤍`")
                if "token" not in st.session_state:
                    result = oauth2.authorize_button(
                        "Connect with Google",
                        REDIRECT_URI,
                        SCOPE,
                        icon="data:image/svg+xml;charset=utf-8,%3Csvg \
                        xmlns='http://www.w3.org/2000/svg' \
                        xmlns:xlink='http://www.w3.org/1999/xlink' \
                        viewBox='0 0 48 48'%3E%3Cdefs%3E%3Cpath id='a' \
                        d='M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 \
                        0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 \
                        2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 \
                        24s9.8 22 22 22c11 0 21-8 21-22 \
                        0-1.3-.2-2.7-.5-4z'/%3E%3C/defs%3E%3CclipPath \
                        id='b'%3E%3Cuse xlink:href='%23a' \
                        overflow='visible'/%3E%3C/clipPath%3E%3Cpath \
                        clip-path='url(%23b)' fill='%23FBBC05' \
                        d='M0 37V11l17 13z'/%3E%3Cpath clip-path='url(%23b)' \
                        fill='%23EA4335' d='M0 11l17 13 7-6.1L48 \
                        14V0H0z'/%3E%3Cpath clip-path='url(%23b)' \
                        fill='%2334A853' d='M0 37l30-23 7.9 1L48 \
                        0v48H0z'/%3E%3Cpath clip-path='url(%23b)' \
                        fill='%234285F4' d='M48 48L17 24l-4-3 \
                        35-10z'/%3E%3C/svg%3E",
                        use_container_width=True,
                    )
                    handle_google_login_if_needed(result)
                    if st.session_state.code:
                        st.rerun()
        with col3:
            pass
    else:
        with st.sidebar:
            display_github_badge()
            display_logo_and_heading()
            st.markdown("`Made with 🤍`")
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
            st.session_state.messages.append(
                {"role": "user", "content": prompt}
            )
            with st.chat_message("user"):
                st.write(prompt)

            prompt_template = PromptTemplate(
                template=TEMPLATE, input_variables=["question"]
            )

            if "model" in st.session_state:
                llm_chain = (
                    prompt_template
                    | st.session_state.model
                    | StrOutputParser()
                )
                if st.session_state.messages[-1]["role"] != "assistant":
                    with st.chat_message("assistant"):
                        with st.spinner("Generating..."):
                            response = llm_chain.invoke(prompt)
                            import re

                            code_block_match = re.search(
                                r"```sql(.*?)```", response, re.DOTALL
                            )
                            if code_block_match:
                                code_block = code_block_match.group(1)
                                st.markdown(
                                    f"```sql\n{code_block}\n```",
                                    unsafe_allow_html=True,
                                )
                                message = {
                                    "role": "assistant",
                                    "content": f"```sql\n{code_block}\n```",
                                }
                                st.session_state.messages.append(message)


if __name__ == "__main__":
    main()
