"""Load ASR vocabulary hints; never rewrite model transcripts with this glossary."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

DEFAULT_GLOSSARY = Path("configs/sacred_terms.json")


def load_glossary(path: Path | None = None) -> dict[str, Any]:
    source = path or DEFAULT_GLOSSARY
    if not source.is_file():
        return {"terms": [], "notes": []}
    data = json.loads(source.read_text(encoding="utf-8"))
    clean_terms = []
    for item in data.get("terms", []):
        if isinstance(item, str) and item.strip():
            clean_terms.append(item.strip())
        elif isinstance(item, dict):
            variants = item.get("variants", [])
            if isinstance(item.get("term"), str):
                variants = [item["term"], *variants]
            clean_terms.extend(v.strip() for v in variants if isinstance(v, str) and v.strip())
    seen: set[str] = set()
    unique = []
    for term in clean_terms:
        marker = term.casefold()
        if marker not in seen:
            unique.append(term)
            seen.add(marker)
    return {"terms": unique, "notes": data.get("notes", [])}


def build_whisper_prompt(glossary: dict[str, Any], max_chars: int = 700) -> str | None:
    """Build compact lexical context; model output is never post-corrected."""
    terms = glossary.get("terms", [])
    if not terms:
        return None
    output = (
        "Speech may contain Sanskrit, Prakrit, shlokas, mantras and Indic religious terms. "
        "Preserve words and script as spoken; do not translate or paraphrase. "
        "Vocabulary hints (not mandatory spellings): "
    )
    for term in terms:
        addition = (", " if not output.endswith(": ") else "") + term
        if len(output) + len(addition) > max_chars:
            break
        output += addition
    return output
