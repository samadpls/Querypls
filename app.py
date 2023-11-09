import streamlit as st
from auth import *


st.set_page_config(page_title="Querypls")
# hiding made with streamlit logo
hide_streamlit_style = (
    """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
)
user_id = None
user_email = None

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "google_login_run" not in st.session_state:
    st.session_state.google_login_run = False
    
with st.sidebar:
    st.title("Querypls")
    code = st.experimental_get_query_params().get("code", None)

    if not st.session_state.google_login_run:
        if code:
            client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
            token = asyncio.run(get_access_token(client, REDIRECT_URI, code))
            user_id, user_email = asyncio.run(get_email(client, token["access_token"]))
            if ["user_id","user_email"] not in st.session_state :
                st.session_state.user_id = user_id
                st.session_state.user_email = user_email
            # Set the flag to indicate that the code has been run
            st.session_state.google_login_run = True
        else:
            st.write(get_login_str(), unsafe_allow_html=True)
    if st.session_state.google_login_run:
        st.success("Google Login credentials already provided!", icon="✅")
        st.write("User ID:", st.session_state.user_id)
        st.write("User Email:", st.session_state.user_email)

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
if prompt := st.chat_input(disabled=(code is None)):
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
