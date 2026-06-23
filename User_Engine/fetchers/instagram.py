import requests

GRAPH = "https://graph.instagram.com"

def fetch_instagram_data(token: dict) -> dict:
    uid = token["user_id"]
    at  = token["access_token"]

    # ── Account stats ──
    profile_resp = requests.get(f"{GRAPH}/{uid}", params={
        "fields": "username,account_type,followers_count,follows_count,media_count",
        "access_token": at,
    })
    profile_resp.raise_for_status()
    profile = profile_resp.json()

    if profile.get("account_type") not in ("BUSINESS", "MEDIA_CREATOR", "CREATOR"):
        raise RuntimeError(
            "Instagram analysis requires a public Business or Creator account."
        )

    # ── Last 20 posts ──
    media_resp = requests.get(f"{GRAPH}/{uid}/media", params={
        "fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink",
        "limit": 20,
        "access_token": at,
    })
    media_resp.raise_for_status()

    recent_posts = []
    for m in media_resp.json().get("data", []):
        recent_posts.append({
            "id":             m.get("id"),
            "caption":        m.get("caption", ""),
            "media_type":     m.get("media_type", ""),
            "timestamp":      m.get("timestamp", ""),
            "like_count":     int(m.get("like_count", 0) or 0),
            "comments_count": int(m.get("comments_count", 0) or 0),
            "permalink":      m.get("permalink", ""),
        })

    return {
        "platform":      "instagram",
        "username":      profile.get("username", ""),
        "account_type":  profile.get("account_type", ""),
        "followers":     int(profile.get("followers_count", 0) or 0),
        "following":     int(profile.get("follows_count", 0) or 0),
        "media_count":   int(profile.get("media_count", 0) or 0),
        "monthly_reach": _safe_monthly_reach(uid, at),
        "recent_posts":  recent_posts,
    }


def _safe_monthly_reach(uid: str, at: str) -> int:
    """Account reach over the last 28 days. Needs instagram_business_manage_insights 
    returns 0 if it doesn't work, so it never breaks the analysis.
    """
    try:
        r = requests.get(f"{GRAPH}/{uid}/insights", params={
            "metric": "reach",
            "period": "days_28",
            "access_token": at,
        })
        if not r.ok:
            return 0
        data = r.json().get("data", [])
        if not data:
            return 0
        item = data[0]
        if "total_value" in item:                
            return int(item["total_value"].get("value", 0) or 0)
        if item.get("values"):                    
            return int(item["values"][-1].get("value", 0) or 0)
    except requests.RequestException:
        pass
    return 0