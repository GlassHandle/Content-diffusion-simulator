from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class TextAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text or caption to analyze.")
    tags: list[str] = Field(default_factory=list, description="Creator hashtags/tags from the get-started form.")

class Composite(BaseModel):
    shareability: float
    saveability: float

class Engagement(BaseModel):
    scores: dict[str, Any]
    composite: Composite
    model: str

class AnalyzeResponse(BaseModel):
    modality: str
    extracted_features: dict[str, Any]
    engagement: Engagement
    topics: dict[str, float]
    entities: list[str]
    tags: list[str]
    content_id: str
    saved_to: str
