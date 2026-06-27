from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .color_analysis import ImageColorAnalyzer
from .schemas import FacesAnalysis, ImageAnalysis
from .vlm import ImageVLMClient

logger = logging.getLogger(__name__)

_OBJECT_SCHEMA = {"type": "object", "properties": {"name": {"type": "string"}, "count": {"type": "integer"}}, "required": ["name", "count"]}
_FACE_SCHEMA = {"type": "object", "properties": {"dominant_emotion": {"type": "string"}, "confidence": {"type": "number"}}, "required": ["dominant_emotion", "confidence"]}
_IMAGE_SCHEMA = {"type": "object", "properties": {"objects": {"type": "array", "items": _OBJECT_SCHEMA}, "face_count": {"type": "integer"}, "faces": {"type": "array", "items": _FACE_SCHEMA}, "visual_appeal_score": {"type": "number"}, "visual_appeal_reasoning": {"type": "string"}, "text_content": {"type": "string"}}, "required": ["objects", "face_count", "faces", "visual_appeal_score", "visual_appeal_reasoning", "text_content"]}
_FACES_SCHEMA = {"type": "object", "properties": {"face_count": {"type": "integer"}, "faces": {"type": "array", "items": _FACE_SCHEMA}}, "required": ["face_count", "faces"]}


class ImageUnderstandingEngine(ImageColorAnalyzer):
    IMAGE_INSTRUCTION = (
        "You are a precise computer-vision analyst. Report only what is visibly "
        "present - never guess or invent. List the distinct object types in the "
        "image and how many of each appear. Count human faces and, for each, give "
        "the single most likely emotion plus your confidence (0-1). Rate overall "
        "visual appeal from 0 (blurry, cluttered, badly composed) to 10 (sharp, "
        "well-composed, striking) and give one short reason. Transcribe any text "
        "visible in the image exactly; return an empty string if there is none. "
        "When a field has nothing to report, return an empty list or empty string "
        "rather than fabricating."
    )
    FACE_INSTRUCTION = (
        "You are a face/emotion analyst. Count the human faces in the image and, "
        "for each, give the single most likely emotion (happy, sad, angry, "
        "surprised, fearful, disgusted, or neutral) and your confidence (0-1). "
        "Report only faces you can actually see; return an empty list if none."
    )

    def __init__(self) -> None:
        self._client = ImageVLMClient()

    def _vlm(self, image_path: str, schema: dict[str, Any], model_cls: type, instruction: str) -> Any:
        return self._client.call(image_path, schema, model_cls, instruction)

    def analyze_faces_and_emotion(self, image_path: str) -> dict[str, Any]:
        try:
            result: FacesAnalysis = self._vlm(image_path, _FACES_SCHEMA, FacesAnalysis, self.FACE_INSTRUCTION)
        except Exception:
            logger.exception("Face analysis failed for %s", image_path)
            return {"face_count": 0, "faces": [], "emotions": []}

        faces = [{"dominant_emotion": f.dominant_emotion, "confidence": round(f.confidence, 3)} for f in result.faces]
        return {"face_count": result.face_count, "faces": faces, "emotions": [f["dominant_emotion"] for f in faces]}

    def process_image(self, image_path: str) -> dict[str, Any]:
        if not Path(image_path).is_file():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info("Processing image: %s", image_path)
        analysis: ImageAnalysis = self._vlm(image_path, _IMAGE_SCHEMA, ImageAnalysis, self.IMAGE_INSTRUCTION)

        objects: dict[str, int] = {}
        for obj in analysis.objects:
            objects[obj.name] = objects.get(obj.name, 0) + obj.count

        return {
            "modality": "image",
            "extracted_features": {
                "objects_detected": objects,
                "faces_detected": analysis.face_count,
                "facial_emotions": [f.dominant_emotion for f in analysis.faces],
                "faces": [{"dominant_emotion": f.dominant_emotion, "confidence": round(f.confidence, 3)} for f in analysis.faces],
                "visual_appeal_score": round(analysis.visual_appeal_score, 1),
                "visual_appeal_reasoning": analysis.visual_appeal_reasoning,
                "color_analysis": self.analyze_color_harmony(image_path),
                "text_content": analysis.text_content.strip(),
            },
        }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
    engine = ImageUnderstandingEngine()
    test_image = "image.jpeg"
    try:
        features = engine.process_image(test_image)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s", exc)
        return
    print(json.dumps(features, indent=2))
