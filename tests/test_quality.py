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


def test_heuristics_are_not_an_accuracy_metric():
    result = assess_transcript_quality("यह एक छोटा परीक्षण है")
    assert "not human review" in result["method_note"]
