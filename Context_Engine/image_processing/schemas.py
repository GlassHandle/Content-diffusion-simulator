from __future__ import annotations

from pydantic import BaseModel, Field


class DetectedObject(BaseModel):
    name: str
    count: int = Field(ge=0)


class DetectedFace(BaseModel):
    dominant_emotion: str
    confidence: float = Field(ge=0.0, le=1.0)


class ImageAnalysis(BaseModel):
    objects: list[DetectedObject]
    face_count: int = Field(ge=0)
    faces: list[DetectedFace]
    visual_appeal_score: float = Field(ge=0.0, le=10.0)
    visual_appeal_reasoning: str
    text_content: str


class FacesAnalysis(BaseModel):
    face_count: int = Field(ge=0)
    faces: list[DetectedFace]
