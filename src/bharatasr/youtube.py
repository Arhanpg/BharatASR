"""Audio-only YouTube downloader adapted from VidTrace's yt-dlp workflow.

Supports a single public video or playlist. It downloads best audio only and
converts it to WAV through FFmpeg; no video stream is downloaded.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse


ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com",
    "music.youtube.com", "youtu.be", "www.youtu.be",
}


def download_youtube_audio(url: str, output_dir: Path) -> list[Path]:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or (parsed.hostname or "").lower() not in ALLOWED_HOSTS:
        raise ValueError("Provide a valid YouTube video or playlist URL.")

    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError("Install YouTube support with: pip install -r requirements-youtube.txt") from exc

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    options = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "noplaylist": False,
        "ignoreerrors": True,
        "quiet": False,
        "no_warnings": False,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "0",
        }],
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=True)
        if not info:
            raise RuntimeError("yt-dlp could not read the supplied YouTube URL.")

    entries = info.get("entries") or [info]
    expected = [
        output_dir / f"{str(entry.get('id'))}.wav"
        for entry in entries
        if entry and entry.get("id")
    ]
    audio_files = [path for path in expected if path.is_file()]
    if not audio_files:
        raise RuntimeError(
            "No audio was downloaded. Check the URL, video availability and FFmpeg installation."
        )
    return audio_files
