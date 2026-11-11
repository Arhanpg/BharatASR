"""Bounded, audio-only YouTube download and deterministic 16 kHz mono conversion."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from typing import Any


ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com",
    "music.youtube.com", "youtu.be", "www.youtu.be",
}


def validate_youtube_url(url: str) -> None:
    parsed = urlparse(url.strip())
    if (
        parsed.scheme not in {"http", "https"}
        or (parsed.hostname or "").lower() not in ALLOWED_HOSTS
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError("Provide a valid public YouTube video or playlist URL.")


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "", value)[:80]


def _convert_to_wav(source: Path, destination: Path) -> None:
    """Convert all models' input to the same mono 16 kHz PCM WAV format."""
    temporary = destination.with_name(destination.stem + ".tmp.wav")
    command = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(source), "-vn", "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le", str(temporary),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=1800)
        if not temporary.is_file() or temporary.stat().st_size < 44:
            raise RuntimeError("FFmpeg did not produce a valid WAV file.")
        temporary.replace(destination)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        temporary.unlink(missing_ok=True)
        detail = getattr(exc, "stderr", "") or str(exc)
        raise RuntimeError(f"Audio conversion failed: {detail[-2000:]}") from exc


def _source_metadata(entry: dict[str, Any], url: str) -> dict[str, Any]:
    return {
        "source": "youtube",
        "video_id": entry.get("id"),
        "title": entry.get("title"),
        "webpage_url": entry.get("webpage_url") or entry.get("url") or url,
        "channel": entry.get("channel") or entry.get("uploader"),
        "channel_id": entry.get("channel_id") or entry.get("uploader_id"),
        "upload_date": entry.get("upload_date"),
        "duration_seconds": entry.get("duration"),
        "source_language_metadata": entry.get("language"),
        "source_audio_language": entry.get("audio_language"),
        "source_availability": entry.get("availability"),
        "extractor": entry.get("extractor"),
    }


def download_youtube_audio(
    url: str,
    output_dir: Path,
    max_videos: int = 20,
) -> list[Path]:
    """Download at most max_videos public entries, cache audio, and normalize to WAV.

    No cookies, login, access-control bypass, or full-video downloads are configured.
    A failed playlist item is logged and skipped without discarding successful audio.
    """
    validate_youtube_url(url)
    if not 1 <= max_videos <= 100:
        raise ValueError("--max-videos must be between 1 and 100.")

    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError(
            "Install YouTube support with: pip install -r requirements-youtube.txt"
        ) from exc

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_options = {
        "quiet": True,
        "no_warnings": False,
        "skip_download": True,
        "extract_flat": False,
        "ignoreerrors": True,
        "noplaylist": False,
        "playlistend": max_videos,
    }
    with yt_dlp.YoutubeDL(metadata_options) as downloader:
        info = downloader.extract_info(url, download=False)
    if not info:
        raise RuntimeError("yt-dlp could not read this YouTube URL.")

    entries = info.get("entries")
    if entries is None:
        entries = [info]
    entries = [entry for entry in entries if entry and entry.get("id")][:max_videos]
    if not entries:
        raise RuntimeError("No accessible video entries were found.")

    audio_paths: list[Path] = []
    failures: list[dict[str, str]] = []
    for entry in entries:
        video_id = _safe_id(str(entry.get("id") or ""))
        if not video_id:
            continue
        destination = output_dir / f"{video_id}.wav"
        metadata_path = output_dir / f"{video_id}.source.json"
        metadata = _source_metadata(entry, url)

        try:
            if not destination.is_file() or destination.stat().st_size < 44:
                download_options = {
                    "format": "bestaudio/best",
                    "outtmpl": str(output_dir / f"{video_id}.%(ext)s"),
                    "noplaylist": True,
                    "ignoreerrors": False,
                    "quiet": False,
                    "no_warnings": False,
                    "continuedl": True,
                    "overwrites": False,
                }
                webpage_url = entry.get("webpage_url")
                if not isinstance(webpage_url, str) or not webpage_url.startswith("http"):
                    webpage_url = f"https://www.youtube.com/watch?v={video_id}"
                with yt_dlp.YoutubeDL(download_options) as downloader:
                    downloader.extract_info(webpage_url, download=True)

                candidates = [
                    path for path in output_dir.glob(f"{video_id}.*")
                    if path.is_file()
                    and path not in {destination, metadata_path}
                    and not path.name.endswith((".part", ".ytdl", ".tmp.wav"))
                ]
                if not candidates:
                    raise RuntimeError("yt-dlp produced no source audio file.")
                source_file = max(candidates, key=lambda path: path.stat().st_mtime)
                _convert_to_wav(source_file, destination)
                source_file.unlink(missing_ok=True)

            metadata["normalized_audio"] = {
                "format": "WAV PCM signed 16-bit",
                "sample_rate_hz": 16000,
                "channels": 1,
                "path": str(destination),
            }
            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            audio_paths.append(destination)
        except Exception as exc:
            failure = {
                "video_id": video_id,
                "title": str(entry.get("title") or ""),
                "error": f"{type(exc).__name__}: {exc}",
            }
            failures.append(failure)
            (output_dir / f"{video_id}.download_error.json").write_text(
                json.dumps(failure, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    if not audio_paths:
        details = "; ".join(item["error"] for item in failures[:3])
        raise RuntimeError(f"No audio could be prepared from this YouTube URL. {details}")
    return audio_paths
