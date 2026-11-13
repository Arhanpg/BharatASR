"""Public AI4Bharat/ARTPARK Hindi Whisper-Small checkpoint."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from bharatasr.backends.base import ASRBackend
from bharatasr.types import TranscriptSegment, TranscriptionResult


class VaaniWhisperHindiBackend(ASRBackend):
    name = "vaani-whisper-hindi"
    model_id = "ARTPARK-IISc/whisper-small-vaani-hindi"

    def __init__(self) -> None:
        try:
            import torch
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError(
                "Install a PyTorch build for your CPU/CUDA environment first, then "
                "run pip install -r requirements-vaani-whisper.txt."
            ) from exc

        self.torch = torch
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device.startswith("cuda") else torch.float32
        self.pipeline: Any = pipeline(
            task="automatic-speech-recognition",
            model=self.model_id,
            chunk_length_s=30,
            device=self.device,
            torch_dtype=dtype,
        )
        # Follow the official model card: force Hindi transcription.
        self.pipeline.model.config.forced_decoder_ids = (
            self.pipeline.tokenizer.get_decoder_prompt_ids(language="hi", task="transcribe")
        )

    def transcribe(self, audio_path: Path, language: str = "hi") -> TranscriptionResult:
        if language.lower() not in {"hi", "hindi"}:
            raise ValueError(
                "ARTPARK-IISc/whisper-small-vaani-hindi is Hindi-specific. "
                "Run with --language hi; use a multilingual backend for other languages."
            )
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)

        started = time.perf_counter()
        try:
            output = self.pipeline(str(path))
        except Exception as exc:
            message = str(exc).casefold()
            is_oom = "out of memory" in message or "cuda oom" in message
            if not self.device.startswith("cuda") or not is_oom:
                raise
            self.pipeline = None
            self.torch.cuda.empty_cache()
            from transformers import pipeline
            self.device = "cpu"
            self.pipeline = pipeline(
                task="automatic-speech-recognition",
                model=self.model_id,
                chunk_length_s=30,
                device="cpu",
                torch_dtype=self.torch.float32,
            )
            self.pipeline.model.config.forced_decoder_ids = (
                self.pipeline.tokenizer.get_decoder_prompt_ids(language="hi", task="transcribe")
            )
            output = self.pipeline(str(path))

        transcript = str(output.get("text", "")).strip()
        return TranscriptionResult(
            backend=self.name,
            model=self.model_id,
            transcript=transcript,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=transcript)] if transcript else [],
            elapsed_seconds=time.perf_counter() - started,
            metadata={
                "device": self.device,
                "language_requested": language,
                "language": "hi",
                "language_detection": "not performed; Hindi is forced by this monolingual checkpoint",
                "long_audio_chunk_length_seconds": 30,
                "licence": "Apache-2.0",
                "note": "Hindi-only Vaani fine-tune; not suitable for Sanskrit or Prakrit.",
            },
        )

    def close(self) -> None:
        self.pipeline = None
        if self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()
