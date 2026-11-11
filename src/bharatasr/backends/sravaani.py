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
        # Official model card uses a single file path string, not a list.
        hypotheses = list(self.model.transcribe(str(path), return_hypotheses=True))
        parts = []
        for hypothesis in hypotheses:
            text = str(getattr(hypothesis, "text", hypothesis)).strip()
            if text:
                parts.append(text)
        text = " ".join(parts).strip()
        return TranscriptionResult(
            backend=self.name, model=self.model_id, transcript=text,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=text)] if text else [],
            elapsed_seconds=time.perf_counter() - start,
            metadata={
                "device": self.device, "language_requested": language,
                "language_detection": "automatic model inference; no language argument exposed by model card",
                "hypothesis_count": len(hypotheses),
                "note": "ASR draft; manually verify mantra spellings and Prakrit words.",
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
