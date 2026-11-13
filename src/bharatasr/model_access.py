"""Authentication helpers for gated Hugging Face checkpoints."""
from __future__ import annotations

import os


def get_huggingface_token() -> str | None:
    token = os.getenv("HF_TOKEN", "").strip()
    if token:
        return token
    try:
        from huggingface_hub import get_token
        return get_token()
    except (ImportError, OSError):
        return None


def is_huggingface_access_error(exc: BaseException) -> bool:
    message = f"{type(exc).__name__}: {exc}".casefold()
    return any(marker in message for marker in (
        "gatedrepoerror", "gated repo", "403 client error", "401 client error",
        "not in the authorized list", "access is restricted",
        "cannot access gated repo", "you are trying to access a gated repo",
    ))


def format_gated_access_error(model_id: str, model_url: str, exc: BaseException) -> str:
    return (
        f"{model_id} could not be downloaded because Hugging Face denied access. "
        "The model did not reach inference; this is not a transcription-quality failure. "
        f"Open {model_url}, sign in, request/accept access and licence terms, then authenticate "
        "in this environment with the Hugging Face CLI login or HF_TOKEN from an approved account. "
        "A token cannot bypass model-owner approval. "
        f"Original error: {type(exc).__name__}: {str(exc)[:1200]}"
    )
