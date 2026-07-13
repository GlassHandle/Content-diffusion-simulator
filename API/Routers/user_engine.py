import json
from pathlib import Path
from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from User_Engine import (authentication, fetchers, scoring)
from .. import db

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "creators"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(
    tags=["Layer 2 - User Engine"]
)


def _safe(user_id: str) -> str:
    """Filesystem-safe version of a client-supplied user_id."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in user_id)


@router.get("/auth/youtube")
def youtube_login(user_id: str = Query(...)):
    """Start YouTube OAuth for a specific user_id."""
    state = db.create_state(user_id, "youtube")
    return RedirectResponse(authentication.yt_get_auth_url(state))


@router.get("/auth/youtube/callback")
def youtube_callback(code: str, state: str):
    mapping = db.consume_state(state)
    if mapping is None:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state.")
    user_id, _ = mapping
    try:
        token = authentication.yt_exchange_code(code, state)  # pass state
        db.save_token(user_id, "youtube", token)
        return {"status": "YouTube connected successfully.", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/auth/instagram")
def instagram_login(user_id: str = Query(...)):
    """Start Instagram OAuth for a specific user_id."""
    state = db.create_state(user_id, "instagram")
    url = authentication.ig_get_auth_url(state)
    return RedirectResponse(url)


@router.get("/auth/instagram/callback")
def instagram_callback(code: str, state: str):
    """Instagram redirects here after consent from the user. Long-lived access token is generated using the code."""
    mapping = db.consume_state(state)
    if mapping is None:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state.")
    user_id, _ = mapping
    try:
        token = authentication.ig_exchange_code(code)
        db.save_token(user_id, "instagram", token)
        return {"status": "Instagram connected successfully.", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/creator/analyze")
def analyze_creator(user_id: str = Query(...)):
    """Fetch the user's connected platforms and return creator scores using the stored tokens."""
    youtube_data = None
    instagram_data = None
    errors = {}

    yt_token = db.get_token(user_id, "youtube")
    if yt_token:
        try:
            creds, fresh = authentication.yt_credentials_from_token(yt_token)
            if creds:
                db.save_token(user_id, "youtube", fresh)
                youtube_data = fetchers.fetch_youtube_data(creds)
        except Exception as e:
            errors["youtube"] = str(e)

    ig_token = db.get_token(user_id, "instagram")
    if ig_token:
        try:
            valid, fresh = authentication.ig_credentials_from_token(ig_token)
            if valid:
                db.save_token(user_id, "instagram", fresh)
                instagram_data = fetchers.fetch_instagram_data(valid)
        except Exception as e:
            errors["instagram"] = str(e)

    if not youtube_data and not instagram_data:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    f"No connected platforms for user_id '{user_id}'. Visit "
                    "/auth/youtube?user_id=... or /auth/instagram?user_id=... first."
                ),
                "errors": errors,
            },
        )

    scores = scoring.compute_scores(youtube_data, instagram_data)

    now = datetime.now(UTC)
    result = {
        "user_id": user_id,
        "analyzed_at": now.strftime("%Y-%m-%d_%H.%M.%S"),
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

    stamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    out_path = OUTPUT_DIR / f"{stamp}-{_safe(user_id)}-creator.json"
    n = 2
    while out_path.exists():
        out_path = OUTPUT_DIR / f"{stamp}-{_safe(user_id)}-{n}-creator.json"
        n += 1
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    db.add_creator_file(user_id, str(out_path))

    return JSONResponse(content=result)
