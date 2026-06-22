import os
import json
import requests
from pathlib import Path

TOKEN_PATH = Path(__file__).resolve().parent.parent / "tokens" / "instagram.json"
TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

CLIENT_ID     = os.getenv("INSTAGRAM_CLIENT_ID")
CLIENT_SECRET = os.getenv("INSTAGRAM_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("INSTAGRAM_REDIRECT_URI", "http://localhost:8000/auth/instagram/callback")

SCOPES = "instagram_basic,instagram_manage_insights,pages_show_list,pages_read_engagement"


def get_auth_url() -> str:
    return (
        f"https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES}"
        f"&response_type=code"
    )


def exchange_code(code: str) -> dict:
    # Step 1: short-lived token
    resp = requests.post(
        "https://graph.facebook.com/v19.0/oauth/access_token",
        data={
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri":  REDIRECT_URI,
            "code":          code,
        },
    )
    resp.raise_for_status()
    short_token = resp.json()["access_token"]

    # Step 2: exchange for long-lived token (60 days)
    resp2 = requests.get(
        "https://graph.facebook.com/v19.0/oauth/access_token",
        params={
            "grant_type":        "fb_exchange_token",
            "client_id":         CLIENT_ID,
            "client_secret":     CLIENT_SECRET,
            "fb_exchange_token": short_token,
        },
    )
    resp2.raise_for_status()
    token_data = resp2.json()
    _save_token(token_data)
    return token_data


def get_token() -> str | None:
    if not TOKEN_PATH.exists():
        return None
    with open(TOKEN_PATH, "r") as f:
        data = json.load(f)
    return data.get("access_token")


def _save_token(data: dict) -> None:
    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f, indent=4)
