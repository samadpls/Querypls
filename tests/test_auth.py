import pytest
from unittest.mock import AsyncMock, patch
from httpx_oauth.clients.google import GoogleOAuth2
from src.constant import *
from src.auth import (
    get_authorization_url,
    get_access_token,
    get_email,
    get_login_str,
)

@pytest.mark.asyncio
async def test_get_authorization_url():
    client = GoogleOAuth2("client_id", "client_secret")
    redirect_uri = "http://example.com/callback"
    with patch.object(client, "get_authorization_url", new=AsyncMock()) as mock_method:
        await get_authorization_url(client, redirect_uri)
        mock_method.assert_called_once_with(
            redirect_uri, scope=["profile", "email"]
        )

@pytest.mark.asyncio
async def test_get_access_token():
    client = GoogleOAuth2("client_id", "client_secret")
    redirect_uri = "http://example.com/callback"
    code = "code"
    with patch.object(client, "get_access_token", new=AsyncMock()) as mock_method:
        await get_access_token(client, redirect_uri, code)
        mock_method.assert_called_once_with(code, redirect_uri)

@pytest.mark.asyncio
async def test_get_email():
    client = GoogleOAuth2("client_id", "client_secret")
    token = "token"
    with patch.object(
        client,
        "get_id_email",
        new=AsyncMock(return_value=("user_id", "user_email")),
    ) as mock_method:
        user_id, user_email = await get_email(client, token)
        mock_method.assert_called_once_with(token)
        assert user_id == "user_id"
        assert user_email == "user_email"

def test_get_login_str():
    with patch("asyncio.run") as mock_run:
        mock_run.return_value = "authorization_url"
        result = get_login_str()
        mock_run.assert_called_once()
        assert '<a href="authorization_url" target="_self">' in result
        assert "Login with Google" in result
