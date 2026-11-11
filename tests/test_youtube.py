import pytest

from bharatasr.youtube import download_youtube_audio, validate_youtube_url


def test_rejects_non_youtube_url_before_importing_downloader(tmp_path):
    with pytest.raises(ValueError, match="public YouTube"):
        download_youtube_audio("https://example.com/video", tmp_path)


def test_rejects_embedded_credentials():
    with pytest.raises(ValueError):
        validate_youtube_url("https://user:password@youtube.com/watch?v=x")


@pytest.mark.parametrize("limit", [0, 101])
def test_video_limit_is_bounded(tmp_path, limit):
    with pytest.raises(ValueError):
        download_youtube_audio("https://youtube.com/watch?v=abc", tmp_path, max_videos=limit)
