from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from bharatasr.quality import assess_transcript_quality, review_flags
from bharatasr.types import TranscriptionResult


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-_")[:70] or "audio"


def create_run_dir(audio_path: Path, output_root: Path = Path("outputs")) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = output_root / f"{stamp}_{safe_slug(audio_path.stem)}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def get_audio_duration(path: Path) -> float | None:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=20, check=False,
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    try:
        import soundfile as sf
        info = sf.info(str(path))
        return float(info.frames / info.samplerate) if info.samplerate else None
    except Exception:
        return None


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\\n", encoding="utf-8")


def summarize_run(rows: list[dict[str, Any]], run_dir: Path | str) -> dict[str, Any]:
    """Aggregate backend outcomes without treating warnings as accurate transcripts."""
    counts = Counter(row.get("status", "unknown") for row in rows)
    generated = counts.get("completed", 0) + counts.get("completed_needs_review", 0)
    status_counts = {
        key: counts.get(key, 0)
        for key in (
            "completed", "completed_needs_review", "empty_output",
            "blocked_access", "skipped", "failed",
        )
    }
    if generated == 0:
        overall = "failed"
    elif any(status_counts[key] for key in ("empty_output", "blocked_access", "skipped", "failed")):
        overall = "partial"
    elif status_counts["completed_needs_review"]:
        overall = "completed_needs_review"
    else:
        overall = "completed"
    return {
        "overall_status": overall,
        "backend_count": len(rows),
        "transcripts_generated": generated,
        "status_counts": status_counts,
        "models": rows,
        "run_dir": str(run_dir),
        "manual_review_required": True,
        "note": (
            "Backend completion only means text was returned and saved. It does not establish "
            "transcript correctness. Inspect quality.json and transcript.review.md; calculate "
            "WER/CER only against a human-verified reference transcript."
        ),
    }


def save_result(
    run_dir: Path,
    result: TranscriptionResult,
    requested_language: str = "auto",
) -> dict[str, Any]:
    model_dir = run_dir / result.backend
    model_dir.mkdir(parents=True, exist_ok=True)
    quality = assess_transcript_quality(
        result.transcript,
        result.metadata,
        audio_duration_seconds=result.metadata.get("audio_duration_seconds"),
    )
    flags = review_flags(result.transcript, requested_language, result.metadata)
    result.metadata["review_required"] = True
    result.metadata["review_flags"] = flags
    result.metadata["transcript_quality"] = quality

    # Preserve the exact model output; never auto-correct or transliterate it.
    write_json(model_dir / "transcript.json", result.to_dict())
    (model_dir / "transcript.txt").write_text(result.transcript + "\\n", encoding="utf-8")
    write_json(model_dir / "segments.json", [
        {
            "index": segment.index,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
            "words": segment.words,
            "language": segment.language,
        }
        for segment in result.segments
    ])
    write_json(model_dir / "quality.json", quality)

    duration = result.metadata.get("audio_duration_seconds")
    rtf = result.elapsed_seconds / duration if duration and duration > 0 else None
    write_json(model_dir / "metrics.json", {
        "backend": result.backend,
        "model": result.model,
        "elapsed_seconds": result.elapsed_seconds,
        "audio_duration_seconds": duration,
        "real_time_factor": rtf,
        "device": result.metadata.get("device"),
        "compute_type": result.metadata.get("compute_type"),
        "metadata": result.metadata,
        "transcript_quality": quality,
    })

    notes = "\\n".join(f"- {flag}" for flag in flags)
    review = (
        f"# Transcript review — {result.backend}\\n\\n"
        f"**Model:** {result.model}\\n\\n"
        f"**Requested language:** {requested_language}\\n\\n"
        f"**Automated screening status:** {quality['status']}\\n\\n"
        "> This screening is heuristic only; it is not WER/CER or a human accuracy review.\\n\\n"
        f"## Review notes\\n\\n{notes}\\n\\n"
        f"## Unmodified model transcript\\n\\n{result.transcript}\\n"
    )
    (model_dir / "transcript.review.md").write_text(review, encoding="utf-8")
    return quality
