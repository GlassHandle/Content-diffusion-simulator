def _score_instagram(data: dict) -> dict:
    followers    = data.get("followers", 0)
    following    = data.get("following", 1)
    media_count  = data.get("media_count", 1)
    recent_posts = data.get("recent_posts", [])
    monthly_reach = data.get("monthly_reach", 0)

    # Engagement rate per post
    engagement_rates = []
    for p in recent_posts:
        likes    = p.get("like_count", 0)
        comments = p.get("comments_count", 0)
        if followers > 0:
            rate = _safe_div(likes + comments, followers)
            engagement_rates.append(rate)

    avg_engagement = (sum(engagement_rates) / len(engagement_rates)) if engagement_rates else 0

    posting_freq = _calc_posting_frequency(
        [p.get("timestamp", "") for p in recent_posts]
    )

    follower_following_ratio = _safe_div(followers, following)

    return {
        "followers":              followers,
        "monthly_reach":          monthly_reach,
        "avg_engagement_rate":    round(avg_engagement, 4),
        "posting_freq_monthly":   round(posting_freq, 2),
        "follower_following_ratio": round(follower_following_ratio, 2),
    }


