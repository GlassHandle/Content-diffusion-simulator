from googleapiclient.discovery import build
from authentication.youtube import get_credentials

def fetch_youtube_data() -> dict:
    creds = get_credentials()
    if not creds:
        raise RuntimeError("No valid YouTube credentials. Complete OAuth first.")

    yt = build("youtube", "v3", credentials=creds)

    # ── Channel stats ──
    channel_resp = yt.channels().list(
        part="snippet,statistics,brandingSettings",
        mine=True,
    ).execute()

    channel = channel_resp["items"][0]
    snippet = channel["snippet"]
    stats   = channel["statistics"]

    # ── Last 20 videos ───
    search_resp = yt.search().list(
        part="id",
        forMine=True,
        type="video",
        order="date",
        maxResults=20,
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]

    videos = []
    if video_ids:
        videos_resp = yt.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids),
        ).execute()

        for v in videos_resp.get("items", []):
            vs = v["statistics"]
            videos.append({
                "id":           v["id"],
                "title":        v["snippet"]["title"],
                "published_at": v["snippet"]["publishedAt"],
                "views":        int(vs.get("viewCount", 0)),
                "likes":        int(vs.get("likeCount", 0)),
                "comments":     int(vs.get("commentCount", 0)),
                "duration":     v["contentDetails"]["duration"],
            })

    return {
        "platform":      "youtube",
        "channel_id":    channel["id"],
        "channel_name":  snippet["title"],
        "description":   snippet.get("description", ""),
        "country":       snippet.get("country", ""),
        "created_at":    snippet["publishedAt"],
        "subscribers":   int(stats.get("subscriberCount", 0)),
        "total_views":   int(stats.get("viewCount", 0)),
        "video_count":   int(stats.get("videoCount", 0)),
        "recent_videos": videos,
    }
