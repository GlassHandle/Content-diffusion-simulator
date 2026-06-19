import json
from datetime import datetime, UTC
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from oauth import youtube as yt_oauth
from rr.kk import instagram as ig_oauth
from fetchers.youtube import fetch_youtube_data
from rr.instagram import fetch_instagram_data
from scoring.scorer import compute_scores

app = FastAPI(title="Creator Intelligence Engine")

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "creators"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────
# OAuth routes
# ──────────────────────────────────────────────────────────────────────

@app.get("/auth/youtube")
def youtube_login():
    """Redirect creator to Google OAuth consent screen."""
    return RedirectResponse(yt_oauth.get_auth_url())


@app.get("/auth/youtube/callback")
def youtube_callback(code: str):
    """Google redirects here after consent. Exchanges code for token."""
    try:
        yt_oauth.exchange_code(code)
        return {"status": "YouTube connected successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/auth/instagram")
def instagram_login():
    """Redirect creator to Meta OAuth consent screen."""
    return RedirectResponse(ig_oauth.get_auth_url())


@app.get("/auth/instagram/callback")
def instagram_callback(code: str):
    """Meta redirects here after consent. Exchanges code for token."""
    try:
        ig_oauth.exchange_code(code)
        return {"status": "Instagram connected successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ──────────────────────────────────────────────────────────────────────
# Scoring route
# ──────────────────────────────────────────────────────────────────────

@app.get("/creator/analyze")
def analyze_creator():
    """
    Fetch data from connected platforms and return creator scores.
    At least one platform must be connected.
    """
    youtube_data   = None
    instagram_data = None
    errors         = {}

    # Try YouTube
    try:
        if yt_oauth.get_credentials():
            youtube_data = fetch_youtube_data()
    except Exception as e:
        errors["youtube"] = str(e)

    # Try Instagram
    try:
        if ig_oauth.get_token():
            instagram_data = fetch_instagram_data()
    except Exception as e:
        errors["instagram"] = str(e)

    if not youtube_data and not instagram_data:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "No connected platforms. Visit /auth/youtube or /auth/instagram first.",
                "errors":  errors,
            },
        )

    scores = compute_scores(youtube_data, instagram_data)

    result = {
        "analyzed_at": datetime.now(UTC).strftime("%Y-%m-%d_%H.%M.%S"),
        "platforms_connected": [
            p for p, d in [("youtube", youtube_data), ("instagram", instagram_data)] if d
        ],
        "scores": {
            "creator_trust_score":      scores["creator_trust_score"],
            "creator_momentum_score":   scores["creator_momentum_score"],
            "creator_momentum_label":   scores["creator_momentum_label"],
            "niche_authority_score":    scores["niche_authority_score"],
            "audience_quality_score":   scores["audience_quality_score"],
            "creator_volatility_score": scores["creator_volatility_score"],
        },
        "raw_metrics": scores["raw"],
        "errors": errors,
    }

    # Save to data/creators/
    filename = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S-creator.json")
    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    return JSONResponse(content=result)


# ──────────────────────────────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    connected = []
    if yt_oauth.get_credentials():
        connected.append("youtube")
    if ig_oauth.get_token():
        connected.append("instagram")
    return {
        "service":   "Creator Intelligence Engine",
        "connected": connected,
        "endpoints": [
            "GET /auth/youtube",
            "GET /auth/instagram",
            "GET /creator/analyze",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
