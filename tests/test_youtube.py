import pytest

from bharatasr.youtube import download_youtube_audio


def test_rejects_non_youtube_url_before_importing_downloader(tmp_path):
    with pytest.raises(ValueError, match="valid YouTube"):
        download_youtube_audio("https://example.com/video", tmp_path)
