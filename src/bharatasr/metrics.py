from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from jiwer import cer, wer


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text).casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def score(reference: str, hypothesis: str) -> dict[str, float | int]:
    ref = normalize_text(reference)
    hyp = normalize_text(hypothesis)
    if not ref:
        raise ValueError("Reference transcript is empty after normalization.")
    return {
        "wer": float(wer(ref, hyp)),
        "cer": float(cer(ref, hyp)),
        "reference_words": len(ref.split()),
        "hypothesis_words": len(hyp.split()),
    }


def compare_run(run_dir: Path, reference_path: Path) -> list[dict]:
    ref = reference_path.read_text(encoding="utf-8")
    rows = []
    for model_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        transcript_path = model_dir / "transcript.txt"
        if not transcript_path.exists():
            continue
        hyp = transcript_path.read_text(encoding="utf-8")
        row = {"backend": model_dir.name, **score(ref, hyp)}
        rows.append(row)
    return rows
