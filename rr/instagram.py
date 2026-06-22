import requests
from oauth.instagram import get_token

GRAPH = "https://graph.facebook.com/v19.0"


def _get(endpoint: str, token: str, params: dict = {}) -> dict:
    resp = requests.get(
        f"{GRAPH}/{endpoint}",
        params={"access_token": token, **params},
    )
    resp.raise_for_status()
    return resp.json()


def fetch_instagram_data() -> dict:
    token = get_token()
    if not token:
        raise RuntimeError("No valid Instagram token. Complete OAuth first.")

    # Get connected IG business account
    me = _get("me", token, {"fields": "id,name,accounts"})
    page_id    = me["accounts"]["data"][0]["id"]
    page_token = me["accounts"]["data"][0]["access_token"]

    ig_resp = _get(page_id, page_token, {"fields": "instagram_business_account"})
    ig_id   = ig_resp["instagram_business_account"]["id"]

    # Account stats
    account = _get(
        ig_id,
        page_token,
        {
            "fields": (
                "id,username,name,biography,followers_count,"
                "follows_count,media_count,profile_picture_url,website"
            )
        },
    )

    # Last 20 posts
    media_resp = _get(
        f"{ig_id}/media",
        page_token,
        {
            "fields": "id,caption,media_type,timestamp,like_count,comments_count",
            "limit":  20,
        },
    )
    posts = media_resp.get("data", [])

    # Audience insights
    insights = _get(
        f"{ig_id}/insights",
        page_token,
        {
            "metric": "reach,impressions,profile_views",
            "period": "month",
        },
    )
    insight_data = {i["name"]: i["values"][-1]["value"] for i in insights.get("data", [])}

    return {
        "platform":            "instagram",
        "ig_id":               account["id"],
        "username":            account.get("username", ""),
        "name":                account.get("name", ""),
        "biography":           account.get("biography", ""),
        "followers":           account.get("followers_count", 0),
        "following":           account.get("follows_count", 0),
        "media_count":         account.get("media_count", 0),
        "monthly_reach":       insight_data.get("reach", 0),
        "monthly_impressions": insight_data.get("impressions", 0),
        "profile_views":       insight_data.get("profile_views", 0),
        "recent_posts":        posts,
    }
