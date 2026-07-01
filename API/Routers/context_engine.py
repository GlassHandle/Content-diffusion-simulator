from __future__ import annotations

import json
import shutil
import tempfile
import uuid
from datetime import datetime, UTC
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from Context_Engine.core.engine import ContentUnderstandingEngine
from Context_Engine.scoring.schemas import TOPICS
from .schemas import AnalyzeResponse, TextAnalyzeRequest
from .. import db

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "content"
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(
    prefix="/context",
    tags=["Layer 3 - Content Understanding"]
)

engine = ContentUnderstandingEngine()

def warmup() -> None:
    _ = engine.text_engine
    _ = engine.image_engine
    _ = engine.video_engine

def _content_vector(result: dict) -> dict:
    eng = result.get("engagement", {}) or {}
    dims = {dim: sc.get("score") for dim, sc in (eng.get("scores") or {}).items()}
    topic_set = set(eng.get("topics") or [])
    return {
        "dims": dims,                                                     
        "composites": eng.get("composite", {}),                          
        "topics": {t: (1.0 if t in topic_set else 0.0) for t in TOPICS},  
        "entities": list(eng.get("entities") or []),                      
    }


def _json_default(o):
    if hasattr(o, "tolist"):   # numpy arrays
        return o.tolist()
    if hasattr(o, "item"):     # numpy scalars
        return o.item()
    return str(o)


def _store_content(username: str, result: dict, vec: dict) -> tuple[str, str]:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    content_id = uuid.uuid4().hex
    path = CONTENT_DIR / f"{content_id}.json"
    record = {
        "content_id": content_id,
        "username": username,
        "created_at": datetime.now(UTC).isoformat(),
        "modality": result.get("modality"),
        **vec,                 
        "analysis": result,     
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, default=_json_default)
    db.add_content_file(content_id, username, str(path), result.get("modality"))
    return content_id, str(path)


def _analyze_and_store(result: dict, username: str) -> dict:
    vec = _content_vector(result)
    content_id, saved_to = _store_content(username, result, vec)
    return {**result, "topics": vec["topics"], "entities": vec["entities"], "content_id": content_id, "saved_to": saved_to}


def _analyze_upload(file: UploadFile, text: str | None, *, is_video: bool) -> dict:
    suffix = Path(file.filename or "").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    file.file.close()
    try:
        if is_video:
            return engine.analyze(video_path=tmp_path, text=text or None)
        return engine.analyze(image_path=tmp_path, text=text or None)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/analyze/text", response_model=AnalyzeResponse)
def analyze_text(body: TextAnalyzeRequest, username: str = Query(...)):
    try:
        result = engine.analyze(text=body.text)
        return _analyze_and_store(result, username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/image", response_model=AnalyzeResponse)
def analyze_image(username: str = Query(...), file: UploadFile = File(...), text: str | None = Form(None)):
    try:
        result = _analyze_upload(file, text, is_video=False)
        return _analyze_and_store(result, username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/video", response_model=AnalyzeResponse)
def analyze_video(username: str = Query(...), file: UploadFile = File(...), text: str | None = Form(None)):
    try:
        result = _analyze_upload(file, text, is_video=True)
        return _analyze_and_store(result, username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content")
def list_content(username: str = Query(...)):
    return db.list_content_files(username)
