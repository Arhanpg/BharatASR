"""Adapter for official Bodhan AI Indic-Transcribe Core/Flex inference.py CLI."""
from __future__ import annotations
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from bharatasr.backends.base import ASRBackend
from bharatasr.types import TranscriptSegment, TranscriptionResult

_DETECTED_LANGUAGE = re.compile(
    r"(?:detected\s+language|language\s+detected)\s*[:=]\s*([A-Za-z][A-Za-z0-9_-]*)",
    re.IGNORECASE,
)


class IndicTranscribeBackend(ASRBackend):
    name = "indictranscribe"

    def __init__(self) -> None:
        self.model_id = os.getenv("INDIC_TRANSCRIBE_MODEL", "bodhan-ai/indic-transcribe-core").strip()
        if self.model_id not in {"bodhan-ai/indic-transcribe-core", "bodhan-ai/indic-transcribe-flex"}:
            raise ValueError("INDIC_TRANSCRIBE_MODEL must be Bodhan Core or Flex.")
        self.device = os.getenv("INDIC_TRANSCRIBE_DEVICE", "cpu").strip().lower()
        if self.device not in {"cpu", "cuda"}:
            raise ValueError("INDIC_TRANSCRIBE_DEVICE must be 'cpu' or 'cuda'.")
        try:
            from huggingface_hub import snapshot_download
        except ImportError as exc:
            raise RuntimeError("Install requirements-indictranscribe.txt first") from exc
        self.model_dir = Path(snapshot_download(repo_id=self.model_id))
        self.inference_script = self.model_dir / "inference.py"
        if not self.inference_script.is_file():
            raise FileNotFoundError(f"Expected official inference.py in {self.model_dir}")

    def transcribe(self, audio_path: Path, language: str = "auto") -> TranscriptionResult:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        command = [sys.executable, str(self.inference_script), str(path)]
        if language.lower() in {"auto", "none", "prakrit"}:
            command.append("--show-lang")
        else:
            command.extend(["--lang", language.lower()])
        child_env = os.environ.copy()
        if self.device == "cpu":
            child_env["CUDA_VISIBLE_DEVICES"] = ""
        started = time.perf_counter()
        process = subprocess.run(
            command, cwd=str(self.model_dir), env=child_env, capture_output=True,
            text=True, encoding="utf-8", errors="replace", check=False,
        )
        elapsed = time.perf_counter() - started
        stdout, stderr = process.stdout.strip(), process.stderr.strip()
        if process.returncode != 0:
            raise RuntimeError(
                f"Indic-Transcribe exited with code {process.returncode}. "
                f"stderr: {stderr[-4000:]} stdout: {stdout[-2000:]}"
            )
        if not stdout:
            raise RuntimeError(f"Indic-Transcribe returned no stdout. stderr: {stderr[-2000:]}")
        lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        transcript = None
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
                "Could not identify transcript line in Indic-Transcribe stdout; "
                f"last lines: {lines[-5:]}"
            )
        match = _DETECTED_LANGUAGE.search(stdout)
        detected = match.group(1) if match else None
        return TranscriptionResult(
            backend=self.name, model=self.model_id, transcript=transcript,
            segments=[TranscriptSegment(index=0, start=None, end=None, text=transcript)],
            elapsed_seconds=elapsed,
            metadata={
                "language_requested": language, "language_detected": detected,
                "language_detection": "official Indic-Transcribe CLI auto-ID"
                    if language.lower() in {"auto", "none", "prakrit"} else "forced language",
                "runner": "official model-packaged inference.py",
                "device_requested": self.device, "model_directory": str(self.model_dir),
                "stdout_full": stdout, "stderr_tail": stderr[-2000:],
                "note": "Supports documented Indic code-mixing and Sanskrit; no dedicated Prakrit mode.",
            },
        )
