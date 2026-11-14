from __future__ import annotations

import unicodedata
from pathlib import Path

import jiwer


def normalize_text(text: str) -> str:
    """Normalize transcripts without deleting Indic-script combining marks.

    Keep Unicode letters, marks (vowel signs/viramas/diacritics), numbers,
    whitespace, and ZWJ/ZWNJ. Replace punctuation and other symbols with spaces.
    """
    text = unicodedata.normalize("NFC", text).casefold()
    kept: list[str] = []
    for character in text:
        category = unicodedata.category(character)
        if (
            character.isspace()
            or category[0] in {"L", "M", "N"}
            or character in {"\u200c", "\u200d"}
        ):
            kept.append(character)
        else:
            kept.append(" ")
    return " ".join("".join(kept).split())


def score(reference: str, hypothesis: str) -> dict[str, float | int]:
    ref = normalize_text(reference)
    hyp = normalize_text(hypothesis)
    if not ref:
        raise ValueError("Reference transcript is empty after normalization.")
    word_details = jiwer.process_words(ref, hyp)
    char_details = jiwer.process_characters(ref, hyp)
    return {
        "wer": float(word_details.wer),
        "cer": float(char_details.cer),
        "reference_words": len(ref.split()),
        "hypothesis_words": len(hyp.split()),
        "substitutions": int(word_details.substitutions),
        "deletions": int(word_details.deletions),
        "insertions": int(word_details.insertions),
        "hits": int(word_details.hits),
        "reference_characters": len(ref),
        "hypothesis_characters": len(hyp),
        "char_substitutions": int(char_details.substitutions),
        "char_deletions": int(char_details.deletions),
        "char_insertions": int(char_details.insertions),
        "char_hits": int(char_details.hits),
    }


def compare_run(run_dir: Path, reference_path: Path) -> list[dict]:
    ref = reference_path.read_text(encoding="utf-8")
    rows = []
    for model_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        if model_dir.name in {"comparison", ".git", "__pycache__"}:
            continue
        transcript_path = model_dir / "transcript.txt"
        if not transcript_path.exists():
            continue
        hyp = transcript_path.read_text(encoding="utf-8")
        row = {"backend": model_dir.name, **score(ref, hyp)}
        rows.append(row)
    return rows
