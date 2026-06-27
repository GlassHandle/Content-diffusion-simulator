from __future__ import annotations

import json
import logging
import os
from typing import Any

from google import genai
from google.genai import types
from pydantic import ValidationError

from .schemas import PrimaryScores

logger = logging.getLogger(__name__)


class LLMScoringLayer:
    MODEL = "gemini-2.5-flash"
    TEMPERATURE = 0.0
    DIMENSIONS = ("humor", "curiosity", "educational", "novelty", "controversy", "emotional_intensity", "relatability", "practical_value")
    SHARE_WEIGHTS = {"emotional_intensity": 0.30, "humor": 0.20, "novelty": 0.20, "relatability": 0.15, "controversy": 0.15}
    SAVE_WEIGHTS = {"practical_value": 0.45, "educational": 0.35, "novelty": 0.20}
    SYSTEM_PROMPT = "You are a content-analysis engine inside a social-media optimization system. You rate content on engagement dimensions using strict, anchored rubrics. You are calibrated and consistent: identical content always receives identical scores. You score how a broad general audience would react, NOT your personal taste. Ground every score in concrete evidence from the features and text you are given; if signal for a dimension is absent, score it low rather than guessing high."
    RUBRIC = """humor               0 = no attempt at humor · 4 = mildly amusing, a small smile ·
                    7 = clearly funny to most people · 10 = exceptional, laugh-out-loud.
curiosity           0 = nothing intriguing · 4 = a mild "huh, interesting" ·
                    7 = a real open loop / information gap that pulls you forward ·
                    10 = irresistible "I NEED to know what happens / how this ends".
educational         0 = teaches nothing · 4 = a minor takeaway ·
                    7 = a clear, useful lesson · 10 = densely informative, viewer
                    learns something genuinely valuable and new.
novelty             0 = generic, seen-a-thousand-times · 4 = a familiar idea with a
                    fresh angle · 7 = distinctly original · 10 = surprising, nothing
                    else looks like this.
controversy         0 = universally agreeable · 4 = mild disagreement possible ·
                    7 = clear opposing camps, heated comments likely ·
                    10 = highly polarizing. (High is NOT "good"; it is just a signal.)
emotional_intensity 0 = flat / neutral · 4 = a noticeable feeling · 7 = strong
                    emotion · 10 = intense high-arousal emotion (awe, anger, joy,
                    fear). Judge AROUSAL, not whether the feeling is positive.
relatability        0 = niche / alienating · 4 = relevant to a specific subgroup ·
                    7 = "that's so me" for a wide audience · 10 = near-universal
                    instant recognition.
practical_value     0 = nothing actionable · 4 = a tip you might use · 7 = a how-to /
                    resource worth keeping · 10 = immediately actionable, you'd save
                    it to do later."""

    def __init__(self, client: genai.Client | None = None) -> None:
        self.client = client or genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        self._validate_weights()

    def score_content(self, feature_payload: dict[str, Any], extra_text: str = "") -> dict[str, Any]:
        prompt = self._build_prompt(feature_payload, extra_text)
        try:
            primary = self._call_model(prompt)
        except ValidationError:
            logger.exception("Gemini returned scores that failed validation.")
            raise
        composite = self._derive_composites(primary)
        return {"scores": {dim: getattr(primary, dim).model_dump() for dim in self.DIMENSIONS}, "composite": composite, "model": self.MODEL}

    def _build_prompt(self, feature_payload: dict[str, Any], extra_text: str) -> str:
        modality = feature_payload.get("modality", "unknown")
        features = feature_payload.get("extracted_features", feature_payload)
        text = extra_text.strip() or self._gather_text(features)
        return f"Analyze this {modality} content and score it.\n\n=== EXTRACTED FEATURES ===\n{json.dumps(features, indent=2)}\n\n=== TEXT / TRANSCRIPT / CAPTION ===\n{text or '(none available)'}\n\n=== SCORING RUBRIC (use these 0-10 anchors) ===\n{self.RUBRIC}\n\nScore every dimension against the rubric, basing each number on the evidence above. Keep each reasoning to a single sentence."

    @staticmethod
    def _gather_text(features: dict[str, Any]) -> str:
        transcript = features.get("transcript")
        candidates = [features.get("text_content"), transcript.get("text") if isinstance(transcript, dict) else transcript, features.get("raw_text")]
        parts = [c for c in candidates if isinstance(c, str) and c.strip()]
        return "\n".join(parts)

    def _call_model(self, prompt: str) -> PrimaryScores:
        response = self.client.models.generate_content(model=self.MODEL, contents=prompt, config=types.GenerateContentConfig(system_instruction=self.SYSTEM_PROMPT, response_mime_type="application/json", response_schema=PrimaryScores, temperature=self.TEMPERATURE))
        return response.parsed or PrimaryScores.model_validate_json(response.text)

    def _derive_composites(self, primary: PrimaryScores) -> dict[str, float]:
        flat = {dim: getattr(primary, dim).score for dim in self.DIMENSIONS}
        shareability = sum(flat[k] * w for k, w in self.SHARE_WEIGHTS.items())
        saveability = sum(flat[k] * w for k, w in self.SAVE_WEIGHTS.items())
        return {"shareability": round(shareability, 1), "saveability": round(saveability, 1)}

    @classmethod
    def _validate_weights(cls) -> None:
        for name, weights in (("SHARE", cls.SHARE_WEIGHTS), ("SAVE", cls.SAVE_WEIGHTS)):
            total = sum(weights.values())
            if abs(total - 1.0) > 1e-6:
                raise ValueError(f"{name}_WEIGHTS sum to {total:.3f}, not 1.0 - composites would fall outside the 0-10 range.")
            unknown = set(weights) - set(cls.DIMENSIONS)
            if unknown:
                raise ValueError(f"{name}_WEIGHTS references unknown dimensions: {unknown}")
