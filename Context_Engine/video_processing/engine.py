from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import cv2
import librosa
import numpy as np
from faster_whisper import WhisperModel
from scenedetect import ContentDetector, SceneManager, open_video

logger = logging.getLogger(__name__)
_TAG_RE = re.compile(r"<[^>]+>")
_TS = r"\d{1,2}:\d{2}(?::\d{2})?[.,]\d{1,3}"
_TIMING_RE = re.compile(rf"({_TS})\s*-->\s*({_TS})")


class VideoUnderstandingEngine:
    WHISPER_SIZE = "base"
    SUBTITLE_EXTENSIONS = (".srt", ".vtt")
    SCENE_THRESHOLD = 27.0
    PACE_BANDS = ((40.0, "frenetic"), (20.0, "fast"), (8.0, "moderate"), (0.0, "slow"))
    AUDIO_SR = 22_050
    MUSIC_FLATNESS_MAX = 0.30
    MUSIC_RMS_MIN = 0.02
    FRAME_SAMPLE_SECONDS = 1.0
    MAX_SAMPLED_FRAMES = 30
    HOOK_WINDOW_SECONDS = 3.0
    HOOK_WEIGHTS = {"opens_with_speech": 0.40, "early_cut": 0.35, "loud_open": 0.25}

    def __init__(self, image_engine: Any | None = None) -> None:
        logger.info("Initializing Whisper (%s)...", self.WHISPER_SIZE)
        self.whisper = WhisperModel(self.WHISPER_SIZE, compute_type="int8")
        self.image_engine = image_engine

    def transcribe(self, video_path: str) -> dict[str, Any]:
        segments_iter, info = self.whisper.transcribe(video_path, beam_size=5)
        segments = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segments_iter]
        return {"language": info.language, "text": " ".join(s["text"] for s in segments), "segments": segments}

    def extract_subtitles(self, video_path: str) -> dict[str, Any]:
        tracks = self._read_sidecar_subtitles(video_path)
        source = "sidecar"
        if not tracks:
            tracks = self._read_embedded_subtitles(video_path)
            source = "embedded"
        if not tracks:
            return {"available": False, "reason": "no subtitle tracks found"}
        full_text = "\n".join(cue["text"] for track in tracks for cue in track["cues"]).strip()
        return {"available": True, "source": source, "track_count": len(tracks), "languages": [t.get("language") for t in tracks], "text": full_text, "tracks": tracks}

    def _read_sidecar_subtitles(self, video_path: str) -> list[dict[str, Any]]:
        video = Path(video_path)
        tracks: list[dict[str, Any]] = []
        for sibling in sorted(video.parent.glob(f"{video.stem}.*")):
            if sibling.suffix.lower() not in self.SUBTITLE_EXTENSIONS:
                continue
            try:
                raw = sibling.read_text(encoding="utf-8", errors="replace")
            except OSError:
                logger.warning("Could not read subtitle file: %s", sibling)
                continue
            cues = self._parse_subtitle_text(raw)
            if cues:
                tracks.append({"language": self._guess_language_from_name(sibling.stem), "format": sibling.suffix.lower().lstrip("."), "cues": cues})
        return tracks

    def _read_embedded_subtitles(self, video_path: str) -> list[dict[str, Any]]:
        tracks: list[dict[str, Any]] = []
        for stream in self._probe_subtitle_streams(video_path):
            srt_text = self._ffmpeg_extract_stream(video_path, stream["index"])
            if not srt_text:
                continue
            cues = self._parse_subtitle_text(srt_text)
            if cues:
                tracks.append({"language": stream.get("language"), "format": "srt", "cues": cues})
        return tracks

    @staticmethod
    def _probe_subtitle_streams(video_path: str) -> list[dict[str, Any]]:
        try:
            out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "s", "-show_entries", "stream=index:stream_tags=language", "-of", "json", video_path], capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            logger.warning("ffprobe could not list subtitle streams: %s", exc)
            return []
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            return []
        return [{"index": s["index"], "language": (s.get("tags") or {}).get("language")} for s in data.get("streams", []) if "index" in s]

    @staticmethod
    def _ffmpeg_extract_stream(video_path: str, stream_index: int) -> str:
        fd, path = tempfile.mkstemp(suffix=".srt")
        os.close(fd)
        try:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video_path, "-map", f"0:{stream_index}", "-f", "srt", path], capture_output=True, text=True, check=True)
            return Path(path).read_text(encoding="utf-8", errors="replace")
        except (OSError, subprocess.CalledProcessError) as exc:
            logger.warning("ffmpeg could not extract subtitle stream %s: %s", stream_index, exc)
            return ""
        finally:
            os.unlink(path)

    def _parse_subtitle_text(self, raw: str) -> list[dict[str, Any]]:
        blocks = re.split(r"\r?\n\r?\n", raw.replace("\ufeff", "").strip())
        cues: list[dict[str, Any]] = []
        for block in blocks:
            lines = [ln for ln in block.splitlines() if ln.strip()]
            if not lines:
                continue
            if lines[0].upper().startswith(("WEBVTT", "NOTE", "STYLE", "REGION")):
                continue
            timing: tuple[float, float] | None = None
            text_lines: list[str] = []
            for line in lines:
                match = _TIMING_RE.search(line)
                if match and timing is None:
                    timing = (self._ts_to_seconds(match.group(1)), self._ts_to_seconds(match.group(2)))
                    continue
                if timing is None and line.strip().isdigit():
                    continue
                if timing is not None:
                    text_lines.append(line)
            text = _TAG_RE.sub("", " ".join(text_lines)).strip()
            if timing and text:
                cues.append({"start": round(timing[0], 2), "end": round(timing[1], 2), "text": text})
        return cues

    @staticmethod
    def _ts_to_seconds(ts: str) -> float:
        ts = ts.replace(",", ".")
        parts = ts.split(":")
        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h, m, s = "0", parts[0], parts[1]
        else:
            return 0.0
        return int(h) * 3600 + int(m) * 60 + float(s)

    @staticmethod
    def _guess_language_from_name(stem: str) -> str | None:
        for token in reversed(stem.split(".")):
            if 2 <= len(token) <= 3 and token.isalpha():
                return token.lower()
        return None

    def analyze_editing_pace(self, video_path: str) -> dict[str, Any]:
        video = open_video(video_path)
        manager = SceneManager()
        manager.add_detector(ContentDetector(threshold=self.SCENE_THRESHOLD))
        manager.detect_scenes(video, show_progress=False)
        scenes = manager.get_scene_list()
        duration = video.duration.get_seconds() if video.duration else 0.0
        cut_count = max(len(scenes) - 1, 0)
        cuts_per_minute = (cut_count / duration * 60.0) if duration else 0.0
        shot_lengths = [(end - start).get_seconds() for start, end in scenes] if scenes else []
        return {"duration_seconds": round(duration, 2), "cut_count": cut_count, "cuts_per_minute": round(cuts_per_minute, 1), "avg_shot_seconds": round(float(np.mean(shot_lengths)), 2) if shot_lengths else None, "pace_label": self._band_label(cuts_per_minute, self.PACE_BANDS), "scene_boundaries": [round((s.get_seconds()), 2) for s, _ in scenes]}

    def analyze_audio(self, video_path: str) -> dict[str, Any]:
        y, sr = librosa.load(video_path, sr=self.AUDIO_SR, mono=True)
        if y.size == 0:
            return {"has_audio": False}
        tempo = float(librosa.beat.beat_track(y=y, sr=sr)[0])
        rms = float(np.mean(librosa.feature.rms(y=y)))
        flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
        likely_music = flatness < self.MUSIC_FLATNESS_MAX and rms > self.MUSIC_RMS_MIN
        return {"has_audio": True, "tempo_bpm": round(tempo, 1), "rms_energy": round(rms, 4), "spectral_flatness": round(flatness, 4), "likely_has_music": likely_music, "trending_audio": self.match_trending_audio(y, sr)}

    def match_trending_audio(self, y: np.ndarray, sr: int) -> dict[str, Any]:
        return {"matched": False, "note": "no trending-audio index configured"}

    def analyze_frame_emotions(self, video_path: str) -> dict[str, Any]:
        if self.image_engine is None:
            return {"available": False, "reason": "no image_engine injected"}
        timeline: list[dict[str, Any]] = []
        emotion_tally: dict[str, int] = {}
        for timestamp, frame_path in self._sample_frames(video_path):
            try:
                result = self.image_engine.analyze_faces_and_emotion(frame_path)
            finally:
                os.unlink(frame_path)
            for emotion in result.get("emotions", []):
                emotion_tally[emotion] = emotion_tally.get(emotion, 0) + 1
            if result.get("emotions"):
                timeline.append({"t": timestamp, "emotions": result["emotions"]})
        dominant = max(emotion_tally, key=emotion_tally.get) if emotion_tally else None
        return {"available": True, "dominant_emotion": dominant, "emotion_tally": emotion_tally, "emotional_arc": timeline}

    def _sample_frames(self, video_path: str):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(int(fps * self.FRAME_SAMPLE_SECONDS), 1)
        frame_idx = 0
        emitted = 0
        try:
            while emitted < self.MAX_SAMPLED_FRAMES:
                ok, frame = cap.read()
                if not ok:
                    break
                if frame_idx % step == 0:
                    fd, path = tempfile.mkstemp(suffix=".jpg")
                    os.close(fd)
                    cv2.imwrite(path, frame)
                    yield round(frame_idx / fps, 2), path
                    emitted += 1
                frame_idx += 1
        finally:
            cap.release()

    def analyze_hook(self, transcript: dict[str, Any], pace: dict[str, Any], audio: dict[str, Any]) -> dict[str, Any]:
        window = self.HOOK_WINDOW_SECONDS
        opening_text = " ".join(seg["text"] for seg in transcript.get("segments", []) if seg["start"] < window).strip()
        opens_with_speech = bool(opening_text)
        early_cut = any(b < window for b in pace.get("scene_boundaries", []))
        loud_open = bool(audio.get("likely_has_music")) or audio.get("rms_energy", 0) > self.MUSIC_RMS_MIN
        signals = {"opens_with_speech": opens_with_speech, "early_cut": early_cut, "loud_open": loud_open}
        score = 10.0 * sum(self.HOOK_WEIGHTS[k] for k, v in signals.items() if v)
        return {"opening_transcript": opening_text, "signals": signals, "heuristic_score": round(score, 1)}

    @staticmethod
    def _band_label(value: float, bands: tuple[tuple[float, str], ...]) -> str:
        for threshold, label in bands:
            if value >= threshold:
                return label
        return bands[-1][1]

    def process_video(self, video_path: str) -> dict[str, Any]:
        if not Path(video_path).is_file():
            raise FileNotFoundError(f"Video not found: {video_path}")
        logger.info("Processing video: %s", video_path)
        transcript = self.transcribe(video_path)
        subtitles = self.extract_subtitles(video_path)
        pace = self.analyze_editing_pace(video_path)
        audio = self.analyze_audio(video_path)
        frame_emotions = self.analyze_frame_emotions(video_path)
        hook = self.analyze_hook(transcript, pace, audio)
        return {"modality": "video", "extracted_features": {"transcript": transcript, "subtitles": subtitles, "editing_pace": pace, "audio": audio, "frame_emotions": frame_emotions, "hook": hook}}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
    engine = VideoUnderstandingEngine()
    print(json.dumps(engine.process_video("video.mp4"), indent=2))
