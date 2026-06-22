import os
from pathlib import Path
import json
import time
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

# Load .env from the project root (one level above this file's folder).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Instagram Login flow, read-only.
# Start with basic only to get the flow working end to end.
# Add "instagram_business_manage_insights" later for account-level reach/views.
SCOPES = [
    "instagram_business_basic",
    # "instagram_business_manage_insights",   # uncomment once basic works
]

TOKEN_PATH = PROJECT_ROOT / "tokens" / "instagram.json"
TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

# MUST be the *Instagram* app ID/secret from
# Meta dashboard -> your app -> Instagram -> "API setup with Instagram login".
# NOT your Facebook App ID.
CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID")
CLIENT_SECRET = os.getenv("INSTAGRAM_CLIENT_SECRET")
REDIRECT_URI = os.getenv(
    "INSTAGRAM_REDIRECT_URI",
    "http://localhost:8000/auth/instagram/callback",
)

# Instagram Login endpoints — never facebook.com here.
AUTH_URL = "https://api.instagram.com/oauth/authorize"      # consent screen
TOKEN_URL = "https://api.instagram.com/oauth/access_token"  # code -> short-lived token
GRAPH = "https://graph.instagram.com"                       # refresh + all data calls


def ig_get_auth_url(state: str = "ig_oauth") -> str:
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": ",".join(SCOPES),
        "response_type": "code",
        "state": state,
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def ig_exchange_code(code: str) -> dict:
    # 1) authorization code -> short-lived token (also returns the IG user id)
    r = requests.post(TOKEN_URL, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code,
    })
    r.raise_for_status()
    short = r.json()
    short_token = short["access_token"]
    ig_user_id = short.get("user_id")

    # 2) short-lived -> long-lived token (~60 days)
    r = requests.get(f"{GRAPH}/access_token", params={
        "grant_type": "ig_exchange_token",
        "client_secret": CLIENT_SECRET,
        "access_token": short_token,
    })
    r.raise_for_status()
    long = r.json()

    token = {
        "access_token": long["access_token"],
        "user_id": ig_user_id,
        "expires_at": time.time() + int(long.get("expires_in", 60 * 24 * 3600)),
    }
    _save_token(token)
    return token


def ig_get_credentials() -> dict | None:
    """Return a valid token dict, refreshing if near expiry. None if not connected.

    Named to match yt_oauth.get_credentials() so main.py calls both the same way.
    """
    if not TOKEN_PATH.exists():
        return None
    token = json.loads(TOKEN_PATH.read_text())
    if token.get("expires_at", 0) - time.time() < 5 * 24 * 3600:
        r = requests.get(f"{GRAPH}/refresh_access_token", params={
            "grant_type": "ig_refresh_token",
            "access_token": token["access_token"],
        })
        if r.ok:
            data = r.json()
            token["access_token"] = data["access_token"]
            token["expires_at"] = time.time() + int(data.get("expires_in", 60 * 24 * 3600))
            _save_token(token)
    return token if token.get("expires_at", 0) > time.time() else None


def _save_token(token: dict) -> None:
    TOKEN_PATH.write_text(json.dumps(token))