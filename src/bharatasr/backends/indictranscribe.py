"""Adapter for the official Bodhan AI Indic-Transcribe Core/Flex inference.py CLI.

The model repository bundles its own inference pipeline. Invoking that script
preserves its audio preprocessing and long-audio chunking implementation.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

from bharatasr.backends.base import ASRBackend
from bharatasr.types import TranscriptSegment, TranscriptionResult


class IndicTranscribeBackend(ASRBackend):
    name = "indictranscribe"

    def __init__(self) -> None:
        self.model_id = os.getenv(
            "INDIC_TRANSCRIBE_MODEL", "bodhan-ai/indic-transcribe-core"
        ).strip()
        if self.model_id not in {
            "bodhan-ai/indic-transcribe-core",
            "bodhan-ai/indic-transcribe-flex",
        }:
            raise ValueError(
                "INDIC_TRANSCRIBE_MODEL must be bodhan-ai/indic-transcribe-core "
                "or bodhan-ai/indic-transcribe-flex"
            )
        self.device = os.getenv("INDIC_TRANSCRIBE_DEVICE", "cpu").strip().lower()
        if self.device not in {"cpu", "cuda"}:
            raise ValueError("INDIC_TRANSCRIBE_DEVICE must be 'cpu' or 'cuda'")

        try:
            from huggingface_hub import snapshot_download
        except ImportError as exc:
            raise RuntimeError("Install requirements-indictranscribe.txt first") from exc
        # A gated model requires accepting its access terms and logging in to HF.
        self.model_dir = Path(snapshot_download(repo_id=self.model_id))
        self.inference_script = self.model_dir / "inference.py"
        if not self.inference_script.is_file():
            raise FileNotFoundError(
                f"Expected official inference.py in downloaded model: {self.inference_script}"
            )

    def transcribe(self, audio_path: Path, language: str = "auto") -> TranscriptionResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)

        command = [sys.executable, str(self.inference_script), str(path)]
        if language.lower() not in {"auto", "none"}:
            command.extend(["--lang", language.lower()])
        else:
            command.append("--show-lang")

        # Keep the 1.2B / ~4.6 GB checkpoint away from a 4 GB GPU by default.
        # To deliberately try GPU inference, set INDIC_TRANSCRIBE_DEVICE=cuda.
        child_env = os.environ.copy()
        if self.device == "cpu":
            child_env["CUDA_VISIBLE_DEVICES"] = ""

        started = time.perf_counter()
        process = subprocess.run(
            command,
            cwd=str(self.model_dir),
            env=child_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        elapsed = time.perf_counter() - started
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        if process.returncode != 0:
            raise RuntimeError(
                f"Indic-Transcribe exited with code {process.returncode}. "
                f"stderr: {stderr[-4000:]} stdout: {stdout[-2000:]}"
            )
        lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        if not lines:
            raise RuntimeError(
                "Indic-Transcribe returned no stdout transcript. "
                f"stderr: {stderr[-2000:]}"
            )

        # The upstream CLI prints a path<TAB>transcript row for each input.
        last_line = lines[-1]
        transcript = last_line.split("\t", 1)[-1].strip()
        transcript = re.sub(
            r"^transcript\s*:\s*", "", transcript, flags=re.IGNORECASE
        )
        if not transcript:
            raise RuntimeError(
                "Could not parse transcript from Indic-Transcribe CLI output. "
                f"Last stdout line: {last_line!r}"
            )

        return TranscriptionResult(
            backend=self.name,
            model=self.model_id,
            transcript=transcript,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=transcript)],
            elapsed_seconds=elapsed,
            metadata={
                "language_requested": language,
                "runner": "official model-packaged inference.py",
                "device_requested": self.device,
                "model_directory": str(self.model_dir),
                "stdout_last_line": last_line,
                "stderr_tail": stderr[-2000:],
                "note": "Utterance-level transcript; stdout/stderr tails are retained for audit.",
            },
        )
