"""Language selection helpers for Indian-language ASR."""
from __future__ import annotations
from dataclasses import dataclass

ALIASES = {
    "auto": None, "detect": None,
    "hindi": "hi", "hi": "hi", "bengali": "bn", "bangla": "bn", "bn": "bn",
    "assamese": "as", "as": "as", "gujarati": "gu", "gu": "gu",
    "kannada": "kn", "kn": "kn", "kashmiri": "ks", "ks": "ks",
    "konkani": "kok", "kok": "kok", "maithili": "mai", "mai": "mai",
    "malayalam": "ml", "ml": "ml", "manipuri": "mni", "mni": "mni",
    "marathi": "mr", "mr": "mr", "nepali": "ne", "ne": "ne",
    "odia": "or", "oriya": "or", "or": "or", "punjabi": "pa", "pa": "pa",
    "sanskrit": "sa", "sa": "sa", "santali": "sat", "sat": "sat",
    "sindhi": "sd", "sd": "sd", "tamil": "ta", "ta": "ta",
    "telugu": "te", "te": "te", "urdu": "ur", "ur": "ur",
    "english": "en", "en": "en", "bhojpuri": "bho", "bho": "bho",
    "bhili": "bhb", "bhb": "bhb", "bodo": "brx", "brx": "brx",
    "dogri": "doi", "doi": "doi",
    "prakrit": "prakrit", "prākrit": "prakrit", "pali-prakrit": "prakrit",
}

@dataclass(frozen=True)
class LanguageRequest:
    original: str
    code: str | None
    is_auto: bool
    needs_review: bool
    note: str | None = None


def resolve_language(value: str) -> LanguageRequest:
    """Resolve language without silently mapping Prakrit to Sanskrit or Hindi."""
    key = value.strip().casefold()
    if key not in ALIASES:
        raise ValueError(f"Unsupported language '{value}'. Use 'auto' or an Indian language name/code.")
    code = ALIASES[key]
    if code == "prakrit":
        return LanguageRequest(
            value, None, True, True,
            "No integrated backend documents a dedicated Prakrit mode. Automatic multilingual recognition is used; manually verify the exact Prakrit variety."
        )
    return LanguageRequest(
        value, code, code is None, code is None,
        "Language is selected automatically; verify the detected language." if code is None else None,
    )
