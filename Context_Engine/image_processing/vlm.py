from __future__ import annotations

import os
from typing import Any

import ollama
from pydantic import BaseModel


class ImageVLMClient:
    MODEL = "qwen3-vl:4b"
    TEMPERATURE = 0.0
    NUM_CTX = 8192
    MAX_IMAGE_DIM = 1280

    def __init__(self) -> None:
        self.client = ollama.Client(host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))

    def call(self, image_path: str, schema: dict[str, Any], model_cls: type[BaseModel], instruction: str) -> Any:
        response = self.client.chat(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": "Analyze this image.", "images": [self.encode_image(image_path)]},
            ],
            format=schema,
            options={"temperature": self.TEMPERATURE, "num_ctx": self.NUM_CTX},
        )
        try:
            content = response.message.content
        except AttributeError:
            content = response["message"]["content"]
        return model_cls.model_validate_json(self.extract_json(content))

    def encode_image(self, image_path: str) -> bytes:
        import cv2

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        h, w = img.shape[:2]
        scale = self.MAX_IMAGE_DIM / max(h, w)
        if scale < 1.0:
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not ok:
            raise ValueError(f"Failed to encode image: {image_path}")
        return buf.tobytes()

    @staticmethod
    def extract_json(text: str) -> str:
        text = text.strip()
        if text.startswith("{"):
            return text
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return text
