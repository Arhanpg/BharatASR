"""Conservative ASR review flags; this module never edits transcript text."""
from __future__ import annotations
from typing import Any


def review_flags(transcript: str, requested_language: str, metadata: dict[str, Any]) -> list[str]:
    flags = [
        "Machine-generated draft: verify against the original audio before quoting or publishing.",
        "Check mantra syllables and Sanskrit/Prakrit terms letter by letter; glossary entries are hints, not corrections.",
    ]
    if not transcript.strip():
        flags.append("No transcript text was produced.")
    if requested_language.strip().casefold() in {"prakrit", "prākrit", "pali-prakrit"}:
        flags.append("Prakrit requested: no integrated backend documents a dedicated Prakrit mode; obtain review from a knowledgeable reader.")
    probability = metadata.get("language_probability_initial")
    if isinstance(probability, (int, float)) and probability < 0.45:
        flags.append(f"Initial language-detection confidence is low ({probability:.2f}); check the detected language.")
    if requested_language.strip().casefold() in {"auto", "detect"}:
        flags.append("Automatically detected language(s) must be checked, especially in recitation and code-switching.")
    return flags
