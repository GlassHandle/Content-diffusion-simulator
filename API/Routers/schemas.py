from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class TextAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text or caption to analyze.")

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
