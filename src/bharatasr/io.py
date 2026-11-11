from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from bharatasr.types import TranscriptionResult


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-_")[:70] or "audio"


def create_run_dir(audio_path: Path, output_root: Path = Path("outputs")) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = output_root / f"{stamp}_{safe_slug(audio_path.stem)}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\\n",
        encoding="utf-8",
    )


def save_result(run_dir: Path, result: TranscriptionResult) -> None:
    model_dir = run_dir / result.backend
    model_dir.mkdir(parents=True, exist_ok=True)
    write_json(model_dir / "transcript.json", result.to_dict())
    (model_dir / "transcript.txt").write_text(result.transcript + "\\n", encoding="utf-8")
    write_json(model_dir / "segments.json", [s.__dict__ for s in result.segments])
    duration = result.metadata.get("audio_duration_seconds")
    rtf = result.elapsed_seconds / duration if duration and duration > 0 else None
    write_json(model_dir / "metrics.json", {
        "backend": result.backend, "model": result.model,
        "elapsed_seconds": result.elapsed_seconds,
        "audio_duration_seconds": duration, "real_time_factor": rtf,
        "device": result.metadata.get("device"),
        "metadata": result.metadata,
    })
