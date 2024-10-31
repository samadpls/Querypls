from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import streamlit as st
import sys
import os
import json
from backend import (
    configure_page_styles,
    display_github_badge,
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

def format_chat_history(messages):
    """Format the chat history as a structured JSON string."""
    history = []
    for msg in messages[1:]:
        content = msg['content']
        if '```sql' in content:
            content = content.replace('```sql\n', '').replace('\n```', '').strip()
        
        history.append({
            "role": msg['role'],
            "query" if msg['role'] == 'user' else "response": content
        })
    
    formatted_history = json.dumps(history, indent=2)
    print("Formatted history:", formatted_history)
    return formatted_history

def extract_sql_code(response):
    """Extract clean SQL code from the response."""
    sql_code_start = response.find("```sql")
    if sql_code_start != -1:
        sql_code_end = response.find("```", sql_code_start + 5)
        if sql_code_end != -1:
            sql_code = response[sql_code_start + 6:sql_code_end].strip()
            return f"```sql\n{sql_code}\n```"
    return response

def main():
    """Main function to configure and run the Querypls application."""
    configure_page_styles("static/css/styles.css")
    
    if "model" not in st.session_state:
        llm = create_huggingface_hub()
        st.session_state["model"] = llm
    
    if "messages" not in st.session_state:
        create_message()
        
    hide_main_menu_and_footer()
    
    with st.sidebar:
        display_github_badge()
        display_logo_and_heading()
        st.markdown("`Made with 🤍`")
        handle_new_chat()
    
    display_welcome_message()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        conversation_history = format_chat_history(st.session_state.messages)
        prompt_template = PromptTemplate(
            template=TEMPLATE,
            input_variables=["input", "conversation_history"]
        )
        
        if "model" in st.session_state:
            llm_chain = prompt_template | st.session_state.model | StrOutputParser()
            
            with st.chat_message("assistant"):
                with st.spinner("Generating..."):
                    response = llm_chain.invoke({
                        "input": prompt,
                        "conversation_history": conversation_history
                    })
                    
                    # Clean and format the response
                    formatted_response = extract_sql_code(response)
                    st.markdown(formatted_response)
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": formatted_response
                    })

if __name__ == "__main__":
    main()