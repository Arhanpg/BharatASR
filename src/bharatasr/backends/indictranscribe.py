"""Bodhan AI Indic-Transcribe Core/Flex backend using the official long-form CLI."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

from bharatasr.backends.base import ASRBackend
from bharatasr.model_access import format_gated_access_error, get_huggingface_token, is_huggingface_access_error
from bharatasr.types import TranscriptSegment, TranscriptionResult

_DETECTED_LANGUAGE = re.compile(
    r"(?:detected\s+language|language\s+detected|language\s*id)\s*[:=]\s*([A-Za-z][A-Za-z0-9_-]*)",
    re.IGNORECASE,
)


class IndicTranscribeBackend(ASRBackend):
    name = "indictranscribe"
    MODEL_IDS = {"bodhan-ai/indic-transcribe-core", "bodhan-ai/indic-transcribe-flex"}

    def __init__(self) -> None:
        self.model_id = os.getenv(
            "INDIC_TRANSCRIBE_MODEL", "bodhan-ai/indic-transcribe-core"
        ).strip()
        if self.model_id not in self.MODEL_IDS:
            raise ValueError(
                "INDIC_TRANSCRIBE_MODEL must be bodhan-ai/indic-transcribe-core "
                "or bodhan-ai/indic-transcribe-flex."
            )
        self.device = os.getenv("INDIC_TRANSCRIBE_DEVICE", "cpu").strip().lower()
        if self.device not in {"cpu", "cuda"}:
            raise ValueError("INDIC_TRANSCRIBE_DEVICE must be cpu or cuda.")
        try:
            from huggingface_hub import snapshot_download
        except ImportError as exc:
            raise RuntimeError("Install requirements-indictranscribe.txt first.") from exc

        try:
            self.model_dir = Path(snapshot_download(
                repo_id=self.model_id, token=get_huggingface_token()
            ))
        except Exception as exc:
            if is_huggingface_access_error(exc):
                raise RuntimeError(format_gated_access_error(
                    self.model_id, f"https://huggingface.co/{self.model_id}", exc
                )) from exc
            raise

        self.inference_script = self.model_dir / "inference.py"
        if not self.inference_script.is_file():
            raise FileNotFoundError(
                f"Official inference.py was not found in model directory: {self.model_dir}"
            )

    def transcribe(self, audio_path: Path, language: str = "auto") -> TranscriptionResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        auto_mode = language.lower() in {"auto", "none", "prakrit"}
        command = [sys.executable, str(self.inference_script), str(path)]
        command.append("--show-lang") if auto_mode else command.extend(["--lang", language.lower()])

        child_env = os.environ.copy()
        if self.device == "cpu":
            child_env["CUDA_VISIBLE_DEVICES"] = ""

        started = time.perf_counter()
        process = subprocess.run(
            command, cwd=str(self.model_dir), env=child_env,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            check=False, timeout=4 * 60 * 60,
        )
        elapsed = time.perf_counter() - started
        stdout, stderr = process.stdout.strip(), process.stderr.strip()
        if process.returncode != 0:
            raise RuntimeError(
                f"Indic-Transcribe exited with code {process.returncode}. "
                f"stderr: {stderr[-4000:]} stdout: {stdout[-2000:]}"
            )
        if not stdout:
            raise RuntimeError(f"Indic-Transcribe returned no transcript output. stderr: {stderr[-2000:]}")

        transcript = None
        lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        for line in reversed(lines):
            if "\t" in line:
                left, right = line.split("\t", 1)
                if path.name.casefold() in left.casefold() or path.stem.casefold() in left.casefold():
                    transcript = right.strip()
                    break
        if transcript is None and len(lines) == 1:
            transcript = lines[0]
        if not transcript:
            raise RuntimeError(
                "Could not identify the transcript line in official Indic-Transcribe output. "
                f"Last stdout lines: {lines[-5:]!r}; stderr tail: {stderr[-1200:]!r}"
            )

        match = _DETECTED_LANGUAGE.search(stdout)
        detected = match.group(1) if match else None
        return TranscriptionResult(
            backend=self.name, model=self.model_id, transcript=transcript,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=transcript)],
            elapsed_seconds=elapsed,
            metadata={
                "language_requested": language,
                "language_detected": detected,
                "language_detection": "official CLI auto-ID" if auto_mode else "forced language",
                "runner": "official bundled inference.py",
                "device_requested": self.device,
                "model_directory": str(self.model_dir),
                "stdout_full": stdout,
                "stderr_tail": stderr[-2000:],
                "long_audio_handling": "official pause-aware chunks of at most 30 seconds with loop recovery",
                "note": "Supports documented Indic code-mixing and Sanskrit; no dedicated Prakrit mode.",
            },
        )
