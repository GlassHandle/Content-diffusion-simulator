from __future__ import annotations

from typing import Any

from Context_Engine.image_processing import ImageUnderstandingEngine
from Context_Engine.scoring import LLMScoringLayer
from Context_Engine.text_processing import TextUnderstandingEngine
from Context_Engine.video_processing import VideoUnderstandingEngine


class ContentUnderstandingEngine:
    def __init__(self) -> None:
        self.scorer = LLMScoringLayer()
        self._image_engine: Any | None = None
        self._text_engine: Any | None = None
        self._video_engine: Any | None = None

    @property
    def image_engine(self) -> Any:
        if self._image_engine is None:
            self._image_engine = ImageUnderstandingEngine()
        return self._image_engine

    @property
    def text_engine(self) -> Any:
        if self._text_engine is None:
            self._text_engine = TextUnderstandingEngine()
        return self._text_engine

    @property
    def video_engine(self) -> Any:
        if self._video_engine is None:
            self._video_engine = VideoUnderstandingEngine(image_engine=self.image_engine)
        return self._video_engine

    def analyze(self, *, image_path: str | None = None, text: str | None = None, video_path: str | None = None) -> dict[str, Any]:
        primary = [v for v in (image_path, text, video_path) if v is not None]
        if len(primary) != 1 and not (video_path or image_path):
            raise ValueError("Provide exactly one primary modality (image/text/video).")
        if video_path is not None:
            payload = self.video_engine.process_video(video_path)
            caption = text or ""
        elif image_path is not None:
            payload = self.image_engine.process_image(image_path)
            caption = text or ""
        else:
            payload = self.text_engine.process_text(text or "")
            caption = ""
        engagement = self.scorer.score_content(payload, extra_text=caption)
        return {"modality": payload["modality"], "extracted_features": payload["extracted_features"], "engagement": engagement}
