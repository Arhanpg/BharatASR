from bharatasr.model_access import (
    format_gated_access_error,
    get_huggingface_token,
    is_huggingface_access_error,
)


def test_explicit_hf_token_is_used(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf-test-token")
    assert get_huggingface_token() == "hf-test-token"


def test_gated_403_is_detected():
    exc = RuntimeError("GatedRepoError: 403 Client Error: not in the authorized list")
    assert is_huggingface_access_error(exc)


def test_access_error_explains_approval_is_required():
    exc = RuntimeError("403 Client Error: access is restricted")
    message = format_gated_access_error(
        "bodhan-ai/indic-transcribe-core",
        "https://huggingface.co/bodhan-ai/indic-transcribe-core",
        exc,
    )
    assert "did not reach inference" in message
    assert "model-owner approval" in message
    assert "Hugging Face CLI login" in message
