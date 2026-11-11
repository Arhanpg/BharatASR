from bharatasr.glossary import build_whisper_prompt, load_glossary


def test_glossary_includes_mantra_spellings():
    prompt = build_whisper_prompt(load_glossary())
    assert prompt
    assert "ह्रीं" in prompt
    assert "HRIM" in prompt
    assert "KLIEM" in prompt


def test_glossary_is_context_not_transcript_rewriter():
    prompt = build_whisper_prompt({"terms": ["ॐ", "ह्रीं"]})
    assert "not mandatory spellings" in prompt
