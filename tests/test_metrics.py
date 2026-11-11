from bharatasr.metrics import normalize_text, score


def test_normalize_text_unicode_and_punctuation():
    assert normalize_text(" नमस्ते, WORLD! ") == "नमस्ते world"


def test_score_identical_text():
    result = score("यह एक परीक्षण है", "यह एक परीक्षण है")
    assert result["wer"] == 0.0
    assert result["cer"] == 0.0


def test_score_nonidentical_text():
    result = score("hello world", "hello there")
    assert result["wer"] > 0
    assert result["cer"] > 0
