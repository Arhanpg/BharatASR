"""AI4Bharat IndicConformer NeMo hybrid RNNT/CTC checkpoint adapter."""
from __future__ import annotations
import os
import time
from pathlib import Path
from bharatasr.backends.base import ASRBackend
from bharatasr.types import TranscriptSegment, TranscriptionResult


class IndicConformerBackend(ASRBackend):
    name = "indicconformer"
    model_id = "AI4Bharat IndicConformer .nemo checkpoint"

    def __init__(self) -> None:
        checkpoint = os.getenv("INDICCONFORMER_CHECKPOINT")
        if not checkpoint:
            raise RuntimeError("Set INDICCONFORMER_CHECKPOINT to a downloaded .nemo checkpoint.")
        self.checkpoint_path = Path(checkpoint)
        if not self.checkpoint_path.is_file():
            raise FileNotFoundError(f"IndicConformer checkpoint not found: {self.checkpoint_path}")
        self.checkpoint_language = os.getenv("INDICCONFORMER_LANGUAGE", "").strip().lower()
        if not self.checkpoint_language:
            raise RuntimeError("Set INDICCONFORMER_LANGUAGE to the language used by this checkpoint.")
        try:
            import nemo.collections.asr as nemo_asr
            import torch
        except ImportError as exc:
            raise RuntimeError("IndicConformer needs the AI4Bharat NeMo fork.") from exc
        self.device = os.getenv("INDICCONFORMER_DEVICE", "cpu").strip().lower()
        if self.device not in {"cpu", "cuda"}:
            raise ValueError("INDICCONFORMER_DEVICE must be 'cpu' or 'cuda'")
        if self.device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("INDICCONFORMER_DEVICE=cuda requested, but CUDA is unavailable.")
        self.model = nemo_asr.models.ASRModel.restore_from(restore_path=str(self.checkpoint_path))
        self.model.eval()
        self.model = self.model.to(self.device)

    def transcribe(self, audio_path: Path, language: str = "auto") -> TranscriptionResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        requested = language.lower()
        if requested not in {"auto", "none"} and requested != self.checkpoint_language:
            raise ValueError(f"Checkpoint language is '{self.checkpoint_language}', but run requested '{requested}'.")
        start = time.perf_counter()
        outputs = self.model.transcribe(audio=[str(path)], batch_size=1, return_hypotheses=False)
        first = outputs[0] if outputs else ""
        text = str(getattr(first, "text", first)).strip()
        return TranscriptionResult(
            backend=self.name, model=self.model_id, transcript=text,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=text)] if text else [],
            elapsed_seconds=time.perf_counter() - start,
            metadata={
                "device": self.device, "language_requested": language,
                "checkpoint_language": self.checkpoint_language,
                "language_detection": "not provided by this checkpoint adapter",
                "checkpoint": str(self.checkpoint_path),
                "review_required": requested in {"auto", "none"},
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
