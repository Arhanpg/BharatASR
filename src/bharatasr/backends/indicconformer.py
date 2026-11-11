"""Advanced AI4Bharat NeMo IndicConformer checkpoint adapter."""
from __future__ import annotations

import os
import time
from pathlib import Path

from bharatasr.backends.base import ASRBackend
from bharatasr.types import TranscriptSegment, TranscriptionResult


class IndicConformerBackend(ASRBackend):
    name = "indicconformer"
    model_id = "ai4bharat/indic-conformer-600m-multilingual"

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
                "IndicConformer needs a separate NeMo-compatible environment. "
                "See the official AI4Bharat instructions."
            ) from exc
        self.model = nemo_asr.models.EncDecCTCModel.restore_from(restore_path=checkpoint)
        self.model.freeze()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)

    def transcribe(self, audio_path: Path, language: str = "hi") -> TranscriptionResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        start = time.perf_counter()
        self.model.cur_decoder = "ctc"
        kwargs = {"batch_size": 1, "logprobs": False}
        if language not in {"auto", "none"}:
            kwargs["language_id"] = language
        output = self.model.transcribe([str(path)], **kwargs)
        text = str(output[0]).strip()
        elapsed = time.perf_counter() - start
        return TranscriptionResult(
            backend=self.name, model=self.model_id, transcript=text,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=text)] if text else [],
            elapsed_seconds=elapsed,
            metadata={"device": self.device, "decoder": "ctc", "language_requested": language},
        )
