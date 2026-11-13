from bharatasr.quality import assess_transcript_quality


def test_empty_output_is_not_clean():
    result = assess_transcript_quality("")
    assert result["status"] == "empty_output"
    assert any("EMPTY OUTPUT" in flag for flag in result["flags"])


def test_long_consecutive_repetition_is_flagged():
    result = assess_transcript_quality(" ".join(["तो"] * 74))
    assert result["status"] == "needs_review"
    assert result["longest_consecutive_token_count"] == 74
    assert any("REPETITION WARNING" in flag for flag in result["flags"])


def test_unicode_replacement_characters_are_flagged():
    result = assess_transcript_quality("नमस्ते � दुनिया")
    assert result["unicode_replacement_character_count"] == 1
    assert any("ENCODING WARNING" in flag for flag in result["flags"])


def test_low_text_yield_is_flagged_when_duration_is_known():
    result = assess_transcript_quality(" ".join(["नमस्ते"] * 60), audio_duration_seconds=600)
    assert result["tokens_per_minute"] == 6.0
    assert any("LOW TEXT YIELD" in flag for flag in result["flags"])


def test_genuine_short_mantra_is_not_auto_rewritten():
    transcript = "ॐ ह्रीं क्लीं ॐ ह्रीं क्लीं"
    result = assess_transcript_quality(transcript, audio_duration_seconds=30)
    assert result["status"] == "no_automatic_flags"
    assert transcript == "ॐ ह्रीं क्लीं ॐ ह्रीं क्लीं"


def test_heuristics_are_not_an_accuracy_metric():
    result = assess_transcript_quality("यह एक छोटा परीक्षण है")
    assert "not human review" in result["method_note"]
