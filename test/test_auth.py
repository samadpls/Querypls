import unittest
from unittest.mock import AsyncMock, patch
from httpx_oauth.clients.google import GoogleOAuth2
from src.constant import *
from src.auth import (
    get_authorization_url,
    get_access_token,
    get_email,
    get_login_str,
)


class TestGoogleOAuth2Methods(unittest.IsolatedAsyncioTestCase):
    async def test_get_authorization_url(self):
        client = GoogleOAuth2("client_id", "client_secret")
        redirect_uri = "http://example.com/callback"
        with patch.object(
            client, "get_authorization_url", new=AsyncMock()
        ) as mock_method:
            await get_authorization_url(client, redirect_uri)
            mock_method.assert_called_once_with(
                redirect_uri, scope=["profile", "email"]
            )

    async def test_get_access_token(self):
        client = GoogleOAuth2("client_id", "client_secret")
        redirect_uri = "http://example.com/callback"
        code = "code"
        with patch.object(client, "get_access_token", new=AsyncMock()) as mock_method:
            await get_access_token(client, redirect_uri, code)
            mock_method.assert_called_once_with(code, redirect_uri)

    async def test_get_email(self):
        client = GoogleOAuth2("client_id", "client_secret")
        token = "token"
        with patch.object(
            client,
            "get_id_email",
            new=AsyncMock(return_value=("user_id", "user_email")),
        ) as mock_method:
            user_id, user_email = await get_email(client, token)
            mock_method.assert_called_once_with(token)
            self.assertEqual(user_id, "user_id")
            self.assertEqual(user_email, "user_email")

    def test_get_login_str(self):
        with patch("asyncio.run") as mock_run:
            mock_run.return_value = "authorization_url"
            result = get_login_str()
            mock_run.assert_called_once()
            self.assertIn('<a href="authorization_url" target="_self">', result)
            self.assertIn("Login with Google", result)


if __name__ == "__main__":
    unittest.main()
