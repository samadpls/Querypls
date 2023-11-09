import streamlit as st
from auth import *


st.set_page_config(page_title="Querypls")
# hiding made with streamlit logo
hide_streamlit_style = (
    """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
)
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


with st.sidebar:
    st.title("Querypls")
    code = st.experimental_get_query_params().get("code", None)

    if code:
        client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
        token = asyncio.run(get_access_token(client, REDIRECT_URI, code))
        user_id, user_email = asyncio.run(get_email(client, token["access_token"]))
        st.success("Google Login credentials already provided!", icon="✅")
        st.write("User ID:", user_id)
        st.write("User Email:", user_email)
    else:
        st.write(get_login_str(), unsafe_allow_html=True)


# Initialise session state variables
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How may I help you?"}
    ]


# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input(disabled=("code" is None)):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = "Testing to make it work"
            placeholder = st.empty()
            full_response = ""
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
