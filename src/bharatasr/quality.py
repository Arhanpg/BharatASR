"""Conservative transcript-quality screening; flags issues but never edits ASR text."""
from __future__ import annotations

from collections import Counter
from typing import Any

_PUNCTUATION = ".,!?;:।॥()[]{}" + '"' + "'“”‘’"


def _tokens(text: str) -> list[str]:
    return [
        token.strip(_PUNCTUATION)
        for token in text.split()
        if token.strip(_PUNCTUATION)
    ]


def assess_transcript_quality(
    transcript: str,
    language_metadata: dict[str, Any] | None = None,
    audio_duration_seconds: float | None = None,
) -> dict[str, Any]:
    """Flag suspicious output; this is not a semantic accuracy score.

    Repetition may be genuine in mantra/recitation. Low token yield may also
    be legitimate for slow speech, music or silence. Flags always need listening.
    """
    metadata = language_metadata or {}
    tokens = _tokens(transcript)
    counts = Counter(tokens)
    unique_count = len(counts)
    unique_ratio = unique_count / len(tokens) if tokens else 0.0
    top_token, top_count = counts.most_common(1)[0] if counts else (None, 0)

    longest_token = None
    longest_run = 0
    current_token = None
    current_run = 0
    for token in tokens:
        if token == current_token:
            current_run += 1
        else:
            current_token, current_run = token, 1
        if current_run > longest_run:
            longest_token, longest_run = token, current_run

    replacement_count = transcript.count(chr(0xFFFD))
    top_ratio = top_count / len(tokens) if tokens else 0.0
    duration = audio_duration_seconds
    if duration is None:
        duration = metadata.get("audio_duration_seconds")
    tokens_per_minute = (
        len(tokens) / (float(duration) / 60.0)
        if isinstance(duration, (int, float)) and duration > 0
        else None
    )

    flags: list[str] = []
    if not transcript.strip():
        flags.append("EMPTY OUTPUT: the backend returned no transcript text.")
    if replacement_count:
        flags.append(
            f"ENCODING WARNING: found {replacement_count} Unicode replacement character(s) (�)."
        )
    if len(tokens) >= 30 and longest_run >= 10:
        flags.append(
            f"REPETITION WARNING: {longest_token!r} occurs {longest_run} times consecutively. "
            "This may indicate a decoding loop; verify against audio because recitation can repeat."
        )
    if len(tokens) >= 100 and unique_ratio < 0.22:
        flags.append(
            f"LOW VOCABULARY DIVERSITY: {unique_count} unique tokens across {len(tokens)} "
            f"(ratio {unique_ratio:.3f}); inspect for loops or repeated output."
        )
    if len(tokens) >= 100 and top_ratio >= 0.12:
        flags.append(
            f"TOKEN DOMINANCE: {top_token!r} accounts for {top_ratio:.1%} of tokens."
        )
    if (
        tokens_per_minute is not None
        and isinstance(duration, (int, float))
        and duration >= 90
        and tokens_per_minute < 40
        and transcript.strip()
    ):
        flags.append(
            f"LOW TEXT YIELD: {tokens_per_minute:.1f} whitespace tokens/minute over "
            f"{duration / 60:.1f} minutes. Check silence, VAD clipping, partial decoding "
            "or unusually slow/chant-like speech."
        )

    probability = metadata.get("language_probability_initial")
    if isinstance(probability, (int, float)) and probability < 0.50:
        flags.append(
            f"LOW LANGUAGE-DETECTION CONFIDENCE: {probability:.3f}; verify the language label."
        )

    status = (
        "empty_output"
        if not transcript.strip()
        else ("needs_review" if flags else "no_automatic_flags")
    )
    return {
        "status": status,
        "manual_review_required": True,
        "character_count": len(transcript),
        "whitespace_token_count": len(tokens),
        "unique_token_count": unique_count,
        "unique_token_ratio": round(unique_ratio, 4),
        "tokens_per_minute": round(tokens_per_minute, 2) if tokens_per_minute is not None else None,
        "most_frequent_token": top_token,
        "most_frequent_token_count": top_count,
        "most_frequent_token_ratio": round(top_ratio, 4),
        "longest_consecutive_token": longest_token,
        "longest_consecutive_token_count": longest_run,
        "unicode_replacement_character_count": replacement_count,
        "language_probability_initial": probability,
        "flags": flags,
        "method_note": (
            "Heuristic screening only. It is not human review, semantic verification, WER or CER. "
            "No automatic flags do not prove correctness."
        ),
    }


def review_flags(
    transcript: str,
    requested_language: str,
    metadata: dict[str, Any],
) -> list[str]:
    flags = [
        "Machine-generated draft: verify against the original audio before quoting or publishing.",
        "Check mantra syllables and Sanskrit/Prakrit terms letter by letter; glossary entries are hints, not corrections.",
    ]
    if requested_language.strip().casefold() in {"prakrit", "prākrit", "pali-prakrit"}:
        flags.append(
            "Prakrit requested: no integrated backend documents a dedicated Prakrit mode; "
            "obtain review from someone familiar with the exact Prakrit variety."
        )
    if requested_language.strip().casefold() in {"auto", "detect"}:
        flags.append(
            "Automatically detected language(s) must be checked, especially in recitation and code-switching."
        )
    flags.extend(
        assess_transcript_quality(
            transcript,
            metadata,
            audio_duration_seconds=metadata.get("audio_duration_seconds"),
        )["flags"]
    )
    return flags
