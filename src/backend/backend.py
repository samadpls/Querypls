"""
Backend utilities for Streamlit configuration and styling.
"""

from config.constants import STREAMLIT_CONFIG
import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def hide_main_menu_and_footer() -> None:
    st.markdown(
        "<style>#MainMenu {visibility: hidden;}        footer {visibility: hidden;}</style>",
        unsafe_allow_html=True,
    )


def display_github_badge() -> None:
    st.markdown(
        "<a href='https://github.com/samadpls/Querypls'><img src='https://img.shields.io/github/stars/samadpls/querypls?color=red&label=star%20me&logoColor=red&style=social'></a>",
        unsafe_allow_html=True,
    )
