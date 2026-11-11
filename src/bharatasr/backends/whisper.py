"""faster-whisper backend adapted from Arhanpg/VidTrace.

The lazy segment generator is consumed inside the guarded inference block so
CUDA iteration errors can trigger a CPU retry.
"""
from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

from bharatasr.backends.base import ASRBackend
from bharatasr.types import TranscriptSegment, TranscriptionResult

log = logging.getLogger(__name__)


def _setup_cuda_dll_paths() -> None:
    if os.name != "nt":
        return
    import sys

    base = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
    if base.is_dir():
        for binary_dir in base.glob("*/bin"):
            try:
                os.add_dll_directory(str(binary_dir))
            except (OSError, AttributeError, ValueError):
                pass
            os.environ["PATH"] = str(binary_dir) + os.pathsep + os.environ.get("PATH", "")


class WhisperBackend(ASRBackend):
    name = "whisper"

    def __init__(self, model_id: str = "medium", prefer_gpu: bool = True) -> None:
        self.model_id = model_id
        self.prefer_gpu = prefer_gpu
        self.model: Any = None
        self.device = "cpu"
        self.compute_type = "int8"
        self._load()

    def _load(self) -> None:
        from faster_whisper import WhisperModel

        _setup_cuda_dll_paths()
        if self.prefer_gpu:
            try:
                import ctranslate2

                supported = ctranslate2.get_supported_compute_types("cuda")
                if ctranslate2.get_cuda_device_count() > 0 and supported:
                    precision = "int8_float16" if "int8_float16" in supported else sorted(supported)[0]
                    self.model = WhisperModel(
                        self.model_id, device="cuda", compute_type=precision,
                        cpu_threads=max(4, os.cpu_count() or 8), num_workers=1,
                    )
                    self.device, self.compute_type = "cuda", precision
                    return
            except Exception as exc:
                log.warning("Whisper CUDA initialization failed; falling back to CPU: %s", exc)
        self._load_cpu()

    def _load_cpu(self) -> None:
        from faster_whisper import WhisperModel

        self.model = WhisperModel(
            self.model_id, device="cpu", compute_type="int8",
            cpu_threads=max(4, os.cpu_count() or 8), num_workers=1,
        )
        self.device, self.compute_type = "cpu", "int8"

    def _decode(self, path: Path, language: str):
        if self.model is None:
            raise RuntimeError("Whisper model is not loaded")
        lang = None if language.lower() in {"auto", "none"} else language
        stream, info = self.model.transcribe(
            str(path), language=lang, task="transcribe",
            beam_size=5, best_of=5, temperature=[0.0, 0.2, 0.4, 0.6],
            compression_ratio_threshold=2.4, log_prob_threshold=-1.0,
            no_speech_threshold=0.6, condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500, "speech_pad_ms": 250},
            word_timestamps=True,
        )
        return list(stream), info

    def transcribe(self, audio_path: Path, language: str = "auto") -> TranscriptionResult:
        audio_path = Path(audio_path)
        if not audio_path.is_file():
            raise FileNotFoundError(audio_path)
        start = time.perf_counter()
        cuda_retry_error = None
        try:
            raw, info = self._decode(audio_path, language)
        except Exception as exc:
            if self.device != "cuda":
                raise
            cuda_retry_error = f"{type(exc).__name__}: {exc}"
            self.model = None
            self._load_cpu()
            raw, info = self._decode(audio_path, language)

        segments = []
        for item in raw:
            text = str(item.text).strip()
            if not text:
                continue
            words = []
            for word in getattr(item, "words", None) or []:
                words.append({
                    "start": float(word.start) if word.start is not None else None,
                    "end": float(word.end) if word.end is not None else None,
                    "word": str(word.word),
                    "probability": float(word.probability) if word.probability is not None else None,
                })
            segments.append(TranscriptSegment(
                index=len(segments), start=float(item.start), end=float(item.end),
                text=text, words=words,
            ))
        elapsed = time.perf_counter() - start
        duration = getattr(info, "duration", None)
        return TranscriptionResult(
            backend=self.name, model=self.model_id,
            transcript=" ".join(s.text for s in segments),
            segments=segments,
            elapsed_seconds=elapsed,
            metadata={
                "language_detected": getattr(info, "language", None),
                "language_probability": getattr(info, "language_probability", None),
                "audio_duration_seconds": duration,
                "device": self.device, "compute_type": self.compute_type,
                "cuda_retry_error": cuda_retry_error,
                "vad_filter": True, "word_timestamps": True,
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
