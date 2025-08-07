import pytest
from unittest.mock import patch, MagicMock
import sys, os
from src.backend import *
from src.constant import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def mock_open():
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        yield mock_open


@pytest.fixture
def mock_markdown():
    with patch("streamlit.markdown") as mock_markdown:
        yield mock_markdown


@pytest.fixture
def mock_set_page_config():
    with patch("streamlit.set_page_config") as mock_set_page_config:
        yield mock_set_page_config


@pytest.fixture
def mock_oauth2_component():
    with patch("streamlit_oauth.OAuth2Component") as mock_oauth2_component:
        yield mock_oauth2_component


def test_hide_main_menu_and_footer(mock_markdown):
    hide_main_menu_and_footer()
    mock_markdown.assert_called_once_with(
        """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>""",
        unsafe_allow_html=True,
    )
