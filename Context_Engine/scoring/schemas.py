from __future__ import annotations
import enum

from pydantic import BaseModel, Field

TOPICS = [
    "comedy", "gaming", "tech", "fitness", "food_cooking", "beauty_fashion", "travel", "music",
    "sports", "education_howto", "news_politics", "finance_business", "art_design", "science",
    "lifestyle_vlog", "parenting_family", "pets_animals", "automotive", "diy_crafts",
    "motivation_selfhelp", "relationships", "nature_outdoors", "film_tv", "health_wellness",
]
TopicEnum = enum.Enum("TopicEnum", {t: t for t in TOPICS})


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
    topics: list[TopicEnum] = Field(
        default_factory=list,
        description="The 1-3 topics from the fixed list that best capture what the content is ABOUT ",
    )
    entities: list[str] = Field(
        default_factory=list,
        description="Specific named subjects the content references (people, events, places, brands, works), "
                    "as a viewer would name them, e.g. 'FIFA World Cup', 'Lionel Messi'. Empty list if none.",
    )
