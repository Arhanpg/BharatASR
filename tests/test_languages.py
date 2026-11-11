from bharatasr.languages import resolve_language


def test_auto_language_detection():
    result = resolve_language("auto")
    assert result.code is None
    assert result.is_auto is True


def test_sanskrit_maps_to_sanskrit_model_code():
    result = resolve_language("Sanskrit")
    assert result.code == "sa"
    assert result.needs_review is False


def test_prakrit_is_never_mapped_to_sanskrit_or_hindi():
    result = resolve_language("Prakrit")
    assert result.code is None
    assert result.is_auto is True
    assert result.needs_review is True
    assert "dedicated Prakrit" in result.note


def test_marathi_alias():
    assert resolve_language("Marathi").code == "mr"
