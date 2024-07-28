import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from src.frontend import (
    display_logo_and_heading,
    display_welcome_message,
    handle_new_chat,
    display_previous_chats,
    create_message,
    update_session_state,
)


@pytest.fixture
def mock_st():
    return MagicMock()


@pytest.fixture
def mock_db():
    return MagicMock()


class MockSessionState:
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


def initialize_session_state(messages=None, key=None, user_email=None):
    st.session_state = MockSessionState()
    st.session_state.messages = messages or []
    st.session_state.key = key
    st.session_state.user_email = user_email


def test_display_logo_and_heading(mock_st):
    with patch.object(st, "image") as mock_image:
        display_logo_and_heading()
        mock_image.assert_called_once_with("static/image/logo.png")


def test_display_welcome_message(mock_st):
    with patch.object(st, "markdown") as mock_markdown:
        with patch.object(st, "session_state", MockSessionState()):
            initialize_session_state(
                messages=[
                    {"role": "assistant", "content": "How may I help you?"}
                ]
            )
            display_welcome_message()
        mock_markdown.assert_called_once_with(
            "#### Welcome to \n ## 🛢💬Querypls - Prompt to SQL"
        )


def test_handle_new_chat(mock_db, mock_st):
    with patch("src.frontend.get_previous_chats") as mock_get_previous_chats:
        mock_get_previous_chats.return_value = []
        with patch.object(st, "markdown") as mock_markdown, patch.object(
            st, "button"
        ) as mock_button:
            with patch.object(st, "session_state", MockSessionState()):
                initialize_session_state(
                    messages=[], user_email="test@example.com"
                )
                handle_new_chat(mock_db, max_chat_histories=5)
            mock_markdown.assert_called_once_with(
                " #### Remaining Chats: `5/5`"
            )
            mock_button.assert_called_once_with("➕ New chat")


def test_create_message():
    with patch.object(st, "session_state", MockSessionState()):
        initialize_session_state(messages=[], key=None)
        create_message()
        assert st.session_state.messages == [
            {"role": "assistant", "content": "How may I help you?"}
        ]
        assert st.session_state.key == "key"


def test_update_session_state(mock_db):
    chat = {"chat": [{"role": "user", "content": "Hello"}], "key": "new_key"}
    with patch.object(st, "session_state", MockSessionState()):
        initialize_session_state(
            messages=[{"role": "assistant", "content": "How may I help you?"}],
            key="old_key",
        )
        with patch("src.frontend.database") as mock_database:
            update_session_state(mock_db, chat)
            mock_database.assert_called_once_with(
                mock_db,
                "old_key",
                [{"role": "assistant", "content": "How may I help you?"}],
            )
            assert st.session_state.messages == chat["chat"]
            assert st.session_state.key == chat["key"]
