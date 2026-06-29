from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from Context_Engine.core.engine import ContentUnderstandingEngine
from .schemas import AnalyzeResponse, TextAnalyzeRequest

router = APIRouter(
    prefix="/context",
    tags=["Layer 3 - Content Understanding"]
)

engine = ContentUnderstandingEngine()

def warmup() -> None:
    _ = engine.text_engine
    _ = engine.image_engine
    _ = engine.video_engine


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
def analyze_text(body: TextAnalyzeRequest):
    try:
        return engine.analyze(text=body.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/image", response_model=AnalyzeResponse)
def analyze_image(file: UploadFile = File(...), text: str | None = Form(None)):
    try:
        return _analyze_upload(file, text, is_video=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/video", response_model=AnalyzeResponse)
def analyze_video(file: UploadFile = File(...), text: str | None = Form(None)):
    try:
        return _analyze_upload(file, text, is_video=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
