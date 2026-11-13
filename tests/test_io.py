import json

from bharatasr.io import save_result
from bharatasr.types import TranscriptSegment, TranscriptionResult


def test_saved_transcript_artifacts_use_real_newlines_and_valid_json(tmp_path):
    result = TranscriptionResult(
        backend="mock",
        model="mock-model",
        transcript="नमस्ते भारत",
        segments=[TranscriptSegment(index=0, start=0.0, end=1.0, text="नमस्ते भारत")],
        metadata={"audio_duration_seconds": 2.0},
        elapsed_seconds=0.5,
    )

    save_result(tmp_path, result, requested_language="hi")
    model_dir = tmp_path / "mock"

    assert (model_dir / "transcript.txt").read_text(encoding="utf-8") == "नमस्ते भारत" + chr(10)
    assert json.loads((model_dir / "transcript.json").read_text(encoding="utf-8"))["transcript"] == "नमस्ते भारत"
    assert json.loads((model_dir / "quality.json").read_text(encoding="utf-8"))["status"] == "no_automatic_flags"
    review = (model_dir / "transcript.review.md").read_text(encoding="utf-8")
    assert chr(10) in review
    assert chr(92) + "n" not in review
