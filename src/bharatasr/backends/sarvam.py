"""Explicitly opt-in Sarvam Saaras hosted API backend.

This can use free signup credits, but the service is metered. It remains
excluded from the default local benchmark and requires two explicit CLI flags.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from bharatasr.backends.base import ASRBackend
from bharatasr.types import TranscriptSegment, TranscriptionResult

LANG_CODES = {
    "hi": "hi-IN", "bn": "bn-IN", "kn": "kn-IN", "ml": "ml-IN",
    "mr": "mr-IN", "or": "od-IN", "od": "od-IN", "pa": "pa-IN",
    "ta": "ta-IN", "te": "te-IN", "gu": "gu-IN", "as": "as-IN",
    "sa": "sa-IN", "ur": "ur-IN", "ne": "ne-IN", "auto": "unknown",
}


class SarvamBackend(ASRBackend):
    name = "sarvam"
    model_id = "saaras:v4"

    def __init__(self) -> None:
        key = os.getenv("SARVAM_API_KEY")
        if not key:
            raise RuntimeError("SARVAM_API_KEY is not set. Sarvam is optional and metered.")
        try:
            from sarvamai import SarvamAI
        except ImportError as exc:
            raise RuntimeError("Install with: pip install sarvamai") from exc
        self.client = SarvamAI(api_subscription_key=key)

    def transcribe(self, audio_path: Path, language: str = "auto") -> TranscriptionResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        code = LANG_CODES.get(language.lower(), language if "-" in language else "unknown")
        start = time.perf_counter()
        with path.open("rb") as stream:
            response = self.client.speech_to_text.transcribe(
                file=stream, model=self.model_id, language_code=code, mode="transcribe"
            )
        text = str(response.transcript).strip()
        elapsed = time.perf_counter() - start
        return TranscriptionResult(
            backend=self.name, model=self.model_id, transcript=text,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=text)] if text else [],
            elapsed_seconds=elapsed,
            metadata={
                "language_requested": language, "language_code": code,
                "service": "hosted metered API", "transcript_mode": "transcribe",
            },
        )
