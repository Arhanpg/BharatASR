"""Project Vaani SraVaani 1.0 local backend (gated Hugging Face checkpoint)."""
from __future__ import annotations

import time
from pathlib import Path

from bharatasr.backends.base import ASRBackend
from bharatasr.model_access import format_gated_access_error, get_huggingface_token, is_huggingface_access_error
from bharatasr.types import TranscriptSegment, TranscriptionResult


class SraVaaniBackend(ASRBackend):
    name = "sravaani"
    model_id = "ARTPARK-IISc/SraVaani-1.0"
    model_url = "https://huggingface.co/ARTPARK-IISc/SraVaani-1.0"

    def __init__(self, device: str = "cpu") -> None:
        try:
            import torch
            from transformers import AutoModel
        except ImportError as exc:
            raise RuntimeError("Install requirements-sravaani.txt first.") from exc
        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("SRAVAANI_DEVICE=cuda requested, but CUDA is unavailable.")
        self.device = device
        try:
            self.model = AutoModel.from_pretrained(
                self.model_id, trust_remote_code=True, token=get_huggingface_token()
            ).to(device).eval()
        except Exception as exc:
            if is_huggingface_access_error(exc):
                raise RuntimeError(format_gated_access_error(self.model_id, self.model_url, exc)) from exc
            raise

    def transcribe(self, audio_path: Path, language: str = "auto") -> TranscriptionResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        started = time.perf_counter()
        # Exact path-based API shown in the current SraVaani model card.
        hypotheses = list(self.model.transcribe(str(path), return_hypotheses=True))
        text_parts = [
            str(getattr(hypothesis, "text", hypothesis)).strip()
            for hypothesis in hypotheses
        ]
        transcript = " ".join(part for part in text_parts if part).strip()
        elapsed = time.perf_counter() - started
        return TranscriptionResult(
            backend=self.name,
            model=self.model_id,
            transcript=transcript,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=transcript)] if transcript else [],
            elapsed_seconds=elapsed,
            metadata={
                "device": self.device,
                "language_requested": language,
                "language_detection": "automatic model inference; model card exposes no language argument",
                "hypothesis_count": len(hypotheses),
                "note": "ASR draft; manually verify Sanskrit, mantra and Prakrit spellings.",
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
