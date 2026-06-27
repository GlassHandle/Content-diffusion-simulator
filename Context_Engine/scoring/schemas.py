from __future__ import annotations

from pydantic import BaseModel, Field


class DimensionScore(BaseModel):
    score: float = Field(ge=0.0, le=10.0, description="0-10 per the rubric anchor.")
    reasoning: str = Field(description="One concise sentence grounding the score.")


class PrimaryScores(BaseModel):
    humor: DimensionScore
    curiosity: DimensionScore
    educational: DimensionScore
    novelty: DimensionScore
    controversy: DimensionScore
    emotional_intensity: DimensionScore
    relatability: DimensionScore
    practical_value: DimensionScore
