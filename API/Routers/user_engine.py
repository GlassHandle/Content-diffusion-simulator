import json
from pathlib import Path
from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from User_Engine import (authentication,fetchers,scoring)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "creators"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(tags=["Layer 2 - Creator Intelligence"])

@router.get("/auth/youtube")
def youtube_login():
    """Redirect creator to Google OAuth consent screen."""
    return RedirectResponse(authentication.yt_get_auth_url())


@router.get("/auth/youtube/callback")
def youtube_callback(code: str):
    """Google redirects here after consent. Exchanges code for token."""
    try:
        authentication.yt_exchange_code(code)
        return {"status": "YouTube connected successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/auth/instagram")
def instagram_login():
    """Redirect creator to Instagram's hosted consent screen."""
    return RedirectResponse(authentication.ig_get_auth_url())


@router.get("/auth/instagram/callback")
def instagram_callback(code: str):
    """Instagram redirects here after consent. Exchanges code for token."""
    try:
        authentication.ig_exchange_code(code)
        return {"status": "Instagram connected successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/creator/analyze")
def analyze_creator():
    """Fetch data from connected platforms and return creator scores."""
    youtube_data   = None
    instagram_data = None
    errors         = {}

    try:
        if authentication.yt_get_credentials():
            youtube_data = fetchers.fetch_youtube_data()
    except Exception as e:
        errors["youtube"] = str(e)

    try:
        if authentication.ig_get_credentials():
            instagram_data = fetchers.fetch_instagram_data()
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

    scores = scoring.compute_scores(youtube_data, instagram_data)

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

    filename = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S-creator.json")
    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    return JSONResponse(content=result)

