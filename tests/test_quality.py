from bharatasr.quality import review_flags


def test_prakrit_is_marked_for_scholarly_review():
    flags = review_flags("अहिंसा", "Prakrit", {})
    assert any("dedicated Prakrit" in flag for flag in flags)


def test_auto_detection_is_marked_for_review():
    flags = review_flags("नमस्ते", "auto", {})
    assert any("Automatically detected" in flag for flag in flags)
