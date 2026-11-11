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
            raise RuntimeError(
                "Set INDICCONFORMER_CHECKPOINT to a downloaded .nemo checkpoint. "
                "See https://github.com/AI4Bharat/IndicConformerASR"
            )
        try:
            import nemo.collections.asr as nemo_asr
            import torch
        except ImportError as exc:
            raise RuntimeError(
                "IndicConformer needs the AI4Bharat NeMo fork. "
                "See https://github.com/AI4Bharat/IndicConformerASR"
            ) from exc

        checkpoint_path = Path(checkpoint)
        if not checkpoint_path.is_file():
            raise FileNotFoundError(f"IndicConformer checkpoint not found: {checkpoint_path}")

        # The released IndicConformer checkpoints are hybrid RNNT/CTC models.
        # NeMo's generic ASRModel loader restores the concrete class from the
        # checkpoint metadata; forcing EncDecCTCModel would reject RNNT models.
        self.model = nemo_asr.models.ASRModel.restore_from(
            restore_path=str(checkpoint_path)
        )
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)

    def transcribe(self, audio_path: Path, language: str = "hi") -> TranscriptionResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        start = time.perf_counter()

        # Use the checkpoint's configured/default hybrid decoder.
        outputs = self.model.transcribe(
            audio=[str(path)], batch_size=1, return_hypotheses=False
        )
        first = outputs[0] if outputs else ""
        text = str(getattr(first, "text", first)).strip()
        elapsed = time.perf_counter() - start
        return TranscriptionResult(
            backend=self.name,
            model=self.model_id,
            transcript=text,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=text)] if text else [],
            elapsed_seconds=elapsed,
            metadata={
                "device": self.device,
                "language_requested": language,
                "decoder": "checkpoint default hybrid decoder",
                "checkpoint": str(checkpoint_path),
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
