from __future__ import annotations

import colorsys
import itertools
from collections import Counter
from typing import Any

import cv2
import numpy as np


class ImageColorAnalyzer:
    PALETTE_SIZE = 5
    PALETTE_SAMPLE_DIM = 200
    MIN_COLOR_PROPORTION = 0.05
    CHROMA_SAT_MIN = 0.20
    CHROMA_VAL_MIN = 0.15
    HIGH_SAT = 0.55
    ANALOGOUS_MAX = 35.0
    COMPLEMENT_TOL = 25.0
    TRIAD_TOL = 20.0
    CLASH_PENALTY = 30.0

    def analyze_color_harmony(self, image_path: str) -> dict[str, Any]:
        palette = self._extract_palette(image_path)
        score, label, warnings = self._score_harmony(palette)
        return {
            "palette": palette,
            "harmony_score": score,
            "harmony_label": label,
            "warnings": warnings,
        }

    def _extract_palette(self, image_path: str) -> list[dict[str, Any]]:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (self.PALETTE_SAMPLE_DIM, self.PALETTE_SAMPLE_DIM), interpolation=cv2.INTER_AREA)
        pixels = image.reshape(-1, 3).astype(np.float32)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.2)
        _, labels, centers = cv2.kmeans(pixels, self.PALETTE_SIZE, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

        counts = np.bincount(labels.flatten(), minlength=self.PALETTE_SIZE)
        proportions = counts / counts.sum()

        palette: list[dict[str, Any]] = []
        for idx in np.argsort(proportions)[::-1]:
            r, g, b = (int(np.clip(c, 0, 255)) for c in centers[idx])
            palette.append(
                {
                    "rgb": (r, g, b),
                    "hex": f"#{r:02x}{g:02x}{b:02x}",
                    "proportion": round(float(proportions[idx]), 3),
                }
            )
        return palette

    def _score_harmony(self, palette: list[dict[str, Any]]) -> tuple[float, str, list[str]]:
        chromatic: list[dict[str, Any]] = []
        for color in palette:
            r, g, b = color["rgb"]
            hue, sat, val = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if (
                sat >= self.CHROMA_SAT_MIN
                and val >= self.CHROMA_VAL_MIN
                and color["proportion"] >= self.MIN_COLOR_PROPORTION
            ):
                chromatic.append(
                    {
                        "hex": color["hex"],
                        "hue": hue * 360.0,
                        "sat": sat,
                        "weight": color["proportion"],
                    }
                )

        if len(chromatic) <= 1:
            return 9.0, "monochromatic / neutral", []

        relationships: list[str] = []
        warnings: list[str] = []
        penalty = 0.0

        for a, b in itertools.combinations(chromatic, 2):
            distance = abs(a["hue"] - b["hue"])
            distance = min(distance, 360.0 - distance)
            relationship = self._classify_hue_pair(distance)
            relationships.append(relationship)

            if relationship == "clash":
                severity = a["weight"] * b["weight"] * a["sat"] * b["sat"]
                penalty += severity * self.CLASH_PENALTY
                if a["sat"] >= self.HIGH_SAT and b["sat"] >= self.HIGH_SAT:
                    warnings.append(
                        f"High-saturation clash between {a['hex']} and {b['hex']} ({distance:.0f} degrees apart)"
                    )

        score = round(max(0.0, min(10.0, 10.0 - penalty)), 1)
        return score, self._dominant_relationship(relationships), warnings

    @staticmethod
    def _classify_hue_pair(distance: float) -> str:
        if distance <= ImageColorAnalyzer.ANALOGOUS_MAX:
            return "analogous"
        if abs(distance - 180.0) <= ImageColorAnalyzer.COMPLEMENT_TOL:
            return "complementary"
        if abs(distance - 120.0) <= ImageColorAnalyzer.TRIAD_TOL:
            return "triadic"
        return "clash"

    @staticmethod
    def _dominant_relationship(relationships: list[str]) -> str:
        counts = Counter(relationships)
        if counts["clash"] and counts["clash"] >= max(counts.values()):
            return "clashing"
        headline = counts.most_common(1)[0][0]
        return "clashing" if headline == "clash" else headline
