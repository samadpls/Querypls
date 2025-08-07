"""
Backend utilities for Streamlit configuration and styling.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.constants import STREAMLIT_CONFIG, HIDE_MENU_STYLE, HIDE_MENU_FOOTER_STYLE, GITHUB_BADGE


def configure_page_styles(file_name: str) -> None:
    st.set_page_config(**STREAMLIT_CONFIG)
    
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.markdown(HIDE_MENU_STYLE, unsafe_allow_html=True)


def hide_main_menu_and_footer() -> None:
    st.markdown(HIDE_MENU_FOOTER_STYLE, unsafe_allow_html=True)


def display_github_badge() -> None:
    st.markdown(GITHUB_BADGE, unsafe_allow_html=True)
