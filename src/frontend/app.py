"""
Main Streamlit application for Querypls.
"""

import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.orchestrator import BackendOrchestrator
from backend.backend import (
    configure_page_styles,
    display_github_badge,
    hide_main_menu_and_footer,
)
from frontend import (
    display_logo_and_heading,
    display_welcome_message,
)
from config.constants import (
    CSV_ANALYSIS_SECTION, CSV_UPLOAD_LABEL, CSV_UPLOAD_HELP, CSV_PREVIEW,
    CSV_COLUMNS, CSV_DTYPES, LOAD_CSV_BUTTON, CSV_LOADED_SUCCESS,
    CSV_UPLOAD_SUCCESS, CSV_UPLOAD_ERROR, SESSION_CREATE_ERROR,
    ORCHESTRATOR_INIT_ERROR, SESSION_NOT_FOUND_ERROR, APP_INIT_ERROR,
    RESPONSE_GENERATION_ERROR, MESSAGE_LOAD_ERROR, MADE_WITH_LOVE, 
    SESSIONS_SECTION, NEW_SESSION_BUTTON
)
from schemas.requests import NewChatRequest


def initialize_orchestrator():
    if "orchestrator" not in st.session_state:
        try:
            st.session_state["orchestrator"] = BackendOrchestrator()
        except Exception as e:
            st.error(ORCHESTRATOR_INIT_ERROR.format(error=str(e)))
            return None
    return st.session_state["orchestrator"]


def get_current_session_id():
    if "current_session_id" not in st.session_state:
        orchestrator = initialize_orchestrator()
        if orchestrator:
            st.session_state["current_session_id"] = orchestrator.get_default_session()
    return st.session_state.get("current_session_id")


def display_messages(session_id: str):
    orchestrator = initialize_orchestrator()
    if not orchestrator:
        return
    
    try:
        conversation = orchestrator.get_conversation_history(session_id)
        for message in conversation.messages:
            with st.chat_message(message.role):
                st.markdown(message.content)
    except Exception as e:
        st.error(MESSAGE_LOAD_ERROR.format(error=str(e)))


def upload_csv_file():
    uploaded_file = st.file_uploader(
        CSV_UPLOAD_LABEL,
        type=['csv'],
        help=CSV_UPLOAD_HELP
    )
    
    if uploaded_file is not None:
        try:
            csv_content = uploaded_file.read().decode('utf-8')
            df = pd.read_csv(uploaded_file)
            st.success(CSV_UPLOAD_SUCCESS.format(shape=df.shape))
            
            with st.expander(CSV_PREVIEW):
                st.dataframe(df.head())
                st.write(CSV_COLUMNS.format(columns=list(df.columns)))
                st.write(CSV_DTYPES.format(dtypes=df.dtypes.to_dict()))
            
            return csv_content
        except Exception as e:
            st.error(CSV_UPLOAD_ERROR.format(error=str(e)))
            return None
    
    return None


def main():
    configure_page_styles("static/css/styles.css")
    
    orchestrator = initialize_orchestrator()
    if not orchestrator:
        st.error(APP_INIT_ERROR)
        return
    
    current_session_id = get_current_session_id()
    if not current_session_id:
        st.error(SESSION_NOT_FOUND_ERROR)
        return
    
    hide_main_menu_and_footer()
    
    with st.sidebar:
        display_github_badge()
        display_logo_and_heading()
        st.markdown(MADE_WITH_LOVE)
        
        st.markdown(SESSIONS_SECTION)
        sessions = orchestrator.list_sessions()
        
        for session in sessions:
            if st.button(
                session.session_name,
                key=f"session_{session.session_id}",
                help=f"Messages: {session.message_count}, Last: {session.last_activity}"
            ):
                st.session_state["current_session_id"] = session.session_id
                st.rerun()
        
        if st.button(NEW_SESSION_BUTTON):
            try:
                new_session = orchestrator.create_new_session(
                    NewChatRequest(session_name=f"Chat {len(sessions) + 1}")
                )
                st.session_state["current_session_id"] = new_session.session_id
                st.rerun()
            except Exception as e:
                st.error(SESSION_CREATE_ERROR.format(error=str(e)))
        
        st.markdown("---")
        st.markdown(CSV_ANALYSIS_SECTION)
        
        csv_content = upload_csv_file()
        if csv_content:
            if st.button(LOAD_CSV_BUTTON):
                try:
                    result = orchestrator.load_csv_data(current_session_id, csv_content)
                    if result["status"] == "success":
                        st.success(CSV_LOADED_SUCCESS)
                        st.session_state["csv_loaded"] = True
                    else:
                        st.error(f"❌ Error loading CSV: {result['message']}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    display_welcome_message()
    display_messages(current_session_id)
    
    if prompt := st.chat_input():
        try:
            csv_loaded = st.session_state.get("csv_loaded", False)
            
            if csv_loaded:
                response = orchestrator.generate_csv_analysis_response(current_session_id, prompt)
            else:
                response = orchestrator.generate_sql_response(current_session_id, prompt)
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(response.content)
                
                if hasattr(response, 'sql_response') and response.sql_response:
                    with st.expander("📊 SQL Details"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Query Type:**", response.sql_response.query_type)
                            st.write("**Complexity:**", response.sql_response.complexity)
                            st.write("**Tables Used:**", ", ".join(response.sql_response.tables_used))
                        with col2:
                            st.write("**Columns:**", ", ".join(response.sql_response.columns_selected))
                            st.write("**Estimated Rows:**", response.sql_response.estimated_rows)
                            if response.sql_response.warnings:
                                st.write("**Warnings:**", ", ".join(response.sql_response.warnings))
        
        except Exception as e:
            st.error(RESPONSE_GENERATION_ERROR.format(error=str(e)))


if __name__ == "__main__":
    main() 