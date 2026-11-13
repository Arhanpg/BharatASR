from pathlib import Path

import pytest

from bharatasr.backends.vaani_whisper_hindi import VaaniWhisperHindiBackend


def test_hindi_only_backend_rejects_other_language_before_model_loading():
    backend = VaaniWhisperHindiBackend.__new__(VaaniWhisperHindiBackend)
    with pytest.raises(ValueError, match="Hindi-specific"):
        backend.transcribe(Path("file-not-needed.wav"), "mr")
