import os
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

TOKEN_PATH = Path(__file__).resolve().parent.parent / "tokens" / "youtube.json"
TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

REDIRECT_URI = os.getenv("YOUTUBE_REDIRECT_URI", "http://localhost:8000/auth/youtube/callback")

CLIENT_CONFIG = {
    "web": {
        "client_id":     os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
        "redirect_uris": [REDIRECT_URI],
        "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
        "token_uri":     "https://oauth2.googleapis.com/token",
    }
}

_flow_store: Flow | None = None


def get_auth_url() -> str:
    global _flow_store
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true",
    )
    _flow_store = flow
    return auth_url


def exchange_code(code: str) -> Credentials:
    global _flow_store
    if _flow_store is None:
        # fallback: create a fresh flow
        flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
    else:
        flow = _flow_store

    flow.fetch_token(code=code)
    creds = flow.credentials
    _save_token(creds)
    _flow_store = None
    return creds


def get_credentials() -> Credentials | None:
    if not TOKEN_PATH.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds)
    return creds if creds and creds.valid else None


def _save_token(creds: Credentials) -> None:
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())