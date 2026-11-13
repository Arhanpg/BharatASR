from pathlib import Path
from types import SimpleNamespace

from bharatasr.backends.whisper import WhisperBackend


class FakeModel:
    def __init__(self):
        self.vad_calls = []

    def transcribe(self, audio_path, **kwargs):
        self.vad_calls.append(kwargs["vad_filter"])
        info = SimpleNamespace(
            duration=15.0,
            duration_after_vad=0.0 if kwargs["vad_filter"] else 15.0,
            language="hi",
            language_probability=0.99,
            all_language_probs=[("hi", 0.99)],
        )
        if kwargs["vad_filter"]:
            return iter([]), info
        segment = SimpleNamespace(
            start=0.0, end=2.5, text="नमस्ते भारत", words=[], language="hi",
            avg_logprob=-0.12, no_speech_prob=0.01, compression_ratio=1.05, temperature=0.0,
        )
        return iter([segment]), info


def test_empty_vad_result_retries_without_vad(tmp_path):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"test audio bytes")
    backend = WhisperBackend.__new__(WhisperBackend)
    backend.model_id = "small"
    backend.initial_prompt = None
    backend.vad_filter = True
    backend.vad_min_silence_duration_ms = 500
    backend.model = FakeModel()
    backend.device = "cpu"
    backend.compute_type = "int8"

    result = backend.transcribe(audio, "hi")

    assert backend.model.vad_calls == [True, False]
    assert result.transcript == "नमस्ते भारत"
    assert result.metadata["vad_fallback_without_vad"] is True
    assert result.metadata["segment_diagnostics"][0]["avg_logprob"] == -0.12
    assert result.metadata["segment_diagnostics"][0]["no_speech_prob"] == 0.01


def test_no_vad_mode_does_not_run_second_pass(tmp_path):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"test audio bytes")
    backend = WhisperBackend.__new__(WhisperBackend)
    backend.model_id = "small"
    backend.initial_prompt = None
    backend.vad_filter = False
    backend.vad_min_silence_duration_ms = 500
    backend.model = FakeModel()
    backend.device = "cpu"
    backend.compute_type = "int8"

    result = backend.transcribe(audio, "hi")

    assert backend.model.vad_calls == [False]
    assert result.transcript == "नमस्ते भारत"
    assert result.metadata["vad_fallback_without_vad"] is False
