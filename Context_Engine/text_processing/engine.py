from __future__ import annotations

import logging
import re
from typing import Any

import textstat
import torch
from transformers import pipeline

logger = logging.getLogger(__name__)


class TextUnderstandingEngine:
    SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
    EMOTION_REPORT_THRESHOLD = 0.10
    READABILITY_BANDS = ((90.0, "very easy"), (70.0, "easy"), (50.0, "fairly difficult"), (30.0, "difficult"), (0.0, "very difficult"))
    TRIGGER_LEXICON: dict[str, tuple[str, ...]] = {
        "curiosity": ("secret", "reveal", "what happens", "you won't believe", "the truth", "nobody tells you", "hidden", "finally"),
        "urgency": ("now", "today", "hurry", "last chance", "don't miss", "before it's too late", "limited", "ends soon"),
        "social_proof": ("everyone", "millions", "viral", "trending", "people are", "the internet", "most popular"),
        "exclusivity": ("only", "exclusive", "members", "invite", "rare", "first time", "behind the scenes"),
        "negativity_bias": ("mistake", "wrong", "stop", "never", "worst", "avoid", "warning", "fail"),
    }

    def __init__(self) -> None:
        logger.info("Initializing text models (weights may download on first run)...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        device_id = 0 if self.device == "cuda" else -1
        logger.info("Text models device: %s", "GPU" if self.device == "cuda" else "CPU")
        self.sentiment = pipeline("sentiment-analysis", model=self.SENTIMENT_MODEL, device=device_id)
        self.emotion = pipeline("text-classification", model=self.EMOTION_MODEL, top_k=None, device=device_id)

    def analyze_sentiment(self, text: str) -> dict[str, Any]:
        result = self.sentiment(text, truncation=True)[0]
        label = result["label"].lower()
        confidence = round(float(result["score"]), 3)
        sign = {"positive": 1.0, "negative": -1.0}.get(label, 0.0)
        return {"label": label, "confidence": confidence, "polarity": round(sign * confidence, 3)}

    def analyze_emotion(self, text: str) -> dict[str, Any]:
        scores = self.emotion(text, truncation=True)[0]
        ranked = sorted(scores, key=lambda s: s["score"], reverse=True)
        distribution = {s["label"]: round(float(s["score"]), 3) for s in ranked if s["score"] >= self.EMOTION_REPORT_THRESHOLD}
        return {"dominant_emotion": ranked[0]["label"], "dominant_confidence": round(float(ranked[0]["score"]), 3), "distribution": distribution}

    def analyze_readability(self, text: str) -> dict[str, Any]:
        flesch = round(textstat.flesch_reading_ease(text), 1)
        return {"flesch_reading_ease": flesch, "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(text), 1), "gunning_fog": round(textstat.gunning_fog(text), 1), "word_count": textstat.lexicon_count(text, removepunct=True), "sentence_count": textstat.sentence_count(text), "reading_time_seconds": round(textstat.reading_time(text, ms_per_char=12), 1), "band": self._readability_band(flesch)}

    @classmethod
    def _readability_band(cls, flesch_score: float) -> str:
        for threshold, label in cls.READABILITY_BANDS:
            if flesch_score >= threshold:
                return label
        return "very difficult"

    def analyze_emotional_triggers(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        fired: dict[str, list[str]] = {}
        for category, phrases in self.TRIGGER_LEXICON.items():
            hits = [p for p in phrases if self._contains_phrase(lowered, p)]
            if hits:
                fired[category] = hits
        return {"trigger_categories": sorted(fired), "matched_phrases": fired, "exclamation_count": text.count("!"), "question_count": text.count("?"), "emotion": self.analyze_emotion(text)}

    @staticmethod
    def _contains_phrase(haystack: str, phrase: str) -> bool:
        return re.search(rf"\b{re.escape(phrase)}\b", haystack) is not None

    def process_text(self, text: str) -> dict[str, Any]:
        text = (text or "").strip()
        if not text:
            raise ValueError("process_text received empty text.")
        logger.info("Processing text (%d chars)", len(text))
        return {"modality": "text", "extracted_features": {"raw_text": text, "sentiment": self.analyze_sentiment(text), "readability": self.analyze_readability(text), "emotional_triggers": self.analyze_emotional_triggers(text)}}
