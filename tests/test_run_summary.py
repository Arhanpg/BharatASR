from bharatasr.io import summarize_run


def test_run_summary_distinguishes_output_warning_empty_and_blocked():
    summary = summarize_run(
        [
            {"backend": "whisper", "status": "completed_needs_review"},
            {"backend": "vaani", "status": "completed"},
            {"backend": "indictranscribe", "status": "blocked_access"},
            {"backend": "sravaani", "status": "empty_output"},
        ],
        "outputs/test-run",
    )
    assert summary["overall_status"] == "partial"
    assert summary["transcripts_generated"] == 2
    assert summary["status_counts"]["blocked_access"] == 1
    assert summary["status_counts"]["empty_output"] == 1


def test_all_empty_or_failed_is_failed():
    summary = summarize_run(
        [
            {"backend": "whisper", "status": "empty_output"},
            {"backend": "sravaani", "status": "blocked_access"},
        ],
        "outputs/test-run",
    )
    assert summary["overall_status"] == "failed"
    assert summary["transcripts_generated"] == 0


def test_unflagged_output_is_not_claimed_accurate():
    summary = summarize_run([{"backend": "whisper", "status": "completed"}], "outputs/test-run")
    assert summary["overall_status"] == "completed"
    assert summary["manual_review_required"] is True
