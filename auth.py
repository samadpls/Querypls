import streamlit as st
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2

CLIENT_ID = "386097294295-cshguegcn7krddrt1mok2srpsqej1d58.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501/"


async def get_authorization_url(client: GoogleOAuth2, redirect_uri: str):
    authorization_url = await client.get_authorization_url(
        redirect_uri, scope=["profile", "email"]
    )
    return authorization_url


async def get_access_token(client: GoogleOAuth2, redirect_uri: str, code: str):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


def get_login_str():
    client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
    authorization_url = asyncio.run(get_authorization_url(client, REDIRECT_URI))
    return f"""<a href="{authorization_url}" target="_self"><button class="button-51" role="button">Login with Google</button></a>"""
