import pytest
from unittest.mock import patch, MagicMock
import sys, os
from src.backend import *
from src.config.constants import *

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
