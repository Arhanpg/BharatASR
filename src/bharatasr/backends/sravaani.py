"""Project Vaani SraVaani 1.0 local backend (gated Hugging Face checkpoint)."""
from __future__ import annotations

import os
import time
from pathlib import Path

from bharatasr.backends.base import ASRBackend
from bharatasr.types import TranscriptSegment, TranscriptionResult


class SraVaaniBackend(ASRBackend):
    name = "sravaani"
    model_id = "ARTPARK-IISc/SraVaani-1.0"

    def __init__(self, device: str = "cpu") -> None:
        token = os.getenv("HF_TOKEN")
        if not token:
            raise RuntimeError(
                "SraVaani is gated. Accept access conditions and create a read token at "
                "https://huggingface.co/ARTPARK-IISc/SraVaani-1.0, then set HF_TOKEN."
            )
        try:
            import torch
            from transformers import AutoModel
        except ImportError as exc:
            raise RuntimeError("Install requirements-sravaani.txt first") from exc

        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("SRAVAANI_DEVICE=cuda requested, but CUDA is unavailable.")
        self.device = device
        self.model = AutoModel.from_pretrained(
            self.model_id, trust_remote_code=True, token=token
        ).to(device).eval()

    def transcribe(self, audio_path: Path, language: str = "auto") -> TranscriptionResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        start = time.perf_counter()
        hypotheses = self.model.transcribe(str(path), return_hypotheses=True)
        text = " ".join(getattr(hyp, "text", str(hyp)) for hyp in hypotheses).strip()
        elapsed = time.perf_counter() - start
        return TranscriptionResult(
            backend=self.name, model=self.model_id, transcript=text,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=text)] if text else [],
            elapsed_seconds=elapsed,
            metadata={
                "device": self.device, "language_requested": language,
                "note": "Official model-card API; current wrapper returns utterance-level text.",
            },
        )

    def close(self) -> None:
        self.model = None
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
