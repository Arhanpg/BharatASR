
"""
YOUTUBE VIDEO SCREENSHOT EXTRACTOR

Input:
    One YouTube video URL

Output:
    One PNG image every 3.5 seconds
    Original video frame resolution
    Lossless PNG images
    Separate output folder for each video
    CSV timestamp manifest

Requirements:
    pip install --upgrade yt-dlp
    FFmpeg installed and available in PATH
"""

import csv
import re
import shutil
import subprocess
import tempfile
import sys

from pathlib import Path
from datetime import datetime
from fractions import Fraction
from urllib.parse import urlparse

import yt_dlp


# ============================================================
# CONFIGURATION
# ============================================================

# Change this to the folder where you want all screenshots.
OUTPUT_ROOT = Path(r"D:\YouTube_Screenshots")

# Screenshot interval in seconds.
INTERVAL_SECONDS = 3.5

# Set to None if FFmpeg is available in Windows PATH.
# Otherwise, specify the full path to ffmpeg.exe.
FFMPEG_EXE = None

# Download the best available video-only stream,
# with best combined format as a fallback.
VIDEO_FORMAT = "bestvideo/best"

# PNG compression level affects file size/speed, not image quality.
PNG_COMPRESSION_LEVEL = "3"


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_ffmpeg_path():
    """Find FFmpeg executable."""

    if FFMPEG_EXE:
        path = Path(FFMPEG_EXE)

        if not path.is_file():
            raise FileNotFoundError(
                f"FFmpeg executable not found: {path}"
            )

        return str(path)

    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise FileNotFoundError(
            "FFmpeg was not found.\n"
            "Install FFmpeg and add its bin directory to PATH."
        )

    return ffmpeg


def validate_youtube_url(url):
    """Validate that the input is a YouTube URL."""

    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()

        valid_host = (
            host == "youtu.be"
            or host == "youtube.com"
            or host.endswith(".youtube.com")
        )

        return (
            parsed.scheme in ("http", "https")
            and valid_host
        )

    except Exception:
        return False


def safe_folder_name(name):
    """Remove characters that are invalid in Windows folder names."""

    name = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        str(name)
    )

    name = re.sub(r"\s+", "_", name)
    name = name.strip("._ ")

    return name[:80] or "youtube_video"


def make_timestamp(milliseconds):
    """Convert milliseconds into a filename-friendly timestamp."""

    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1_000)

    return (
        f"{hours:02d}h"
        f"{minutes:02d}m"
        f"{seconds:02d}s"
        f"{millis:03d}ms"
    )


def create_output_folder(title, video_id):
    """Create a unique folder for this extraction."""

    safe_title = safe_folder_name(title)
    run_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    folder_name = (
        f"{safe_title}_{video_id}_{run_time}"
    )

    output_folder = OUTPUT_ROOT / folder_name
    output_folder.mkdir(parents=True, exist_ok=True)

    return output_folder


# ============================================================
# YOUTUBE DOWNLOAD
# ============================================================

def download_youtube_video(url, temporary_folder):
    """
    Download the best available video stream.

    Audio is not required for screenshot extraction.
    """

    print("\n" + "=" * 65)
    print("DOWNLOADING YOUTUBE VIDEO")
    print("=" * 65)

    output_template = str(
        Path(temporary_folder) / "%(id)s.%(ext)s"
    )

    ydl_options = {
        "format": VIDEO_FORMAT,
        "outtmpl": output_template,

        # Process one video, not the entire playlist.
        "noplaylist": True,

        # Download reliability.
        "retries": 10,
        "fragment_retries": 10,
        "socket_timeout": 30,

        # Replace incomplete or previous temporary downloads.
        "overwrites": True,
        "continuedl": True,

        "quiet": False,
        "no_warnings": False,
    }

    with yt_dlp.YoutubeDL(ydl_options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        if not info:
            raise RuntimeError(
                "Unable to retrieve YouTube video information."
            )

        video_path = Path(
            info.get("filepath")
            or info.get("_filename")
            or ydl.prepare_filename(info)
        )

    # Fallback in case the final filename differs.
    if not video_path.is_file():

        candidates = [
            p for p in Path(temporary_folder).iterdir()
            if p.is_file()
            and p.suffix.lower() not in (
                ".part", ".ytdl", ".json"
            )
        ]

        if not candidates:
            raise FileNotFoundError(
                "Downloaded video file could not be located."
            )

        video_path = max(
            candidates,
            key=lambda p: p.stat().st_size
        )

    print("\nDownload completed!")
    print(f"Video title: {info.get('title', 'Unknown')}")
    print(f"Video ID: {info.get('id', 'Unknown')}")

    width = info.get("width")
    height = info.get("height")

    if width and height:
        print(f"Video resolution: {width} x {height}")

    if info.get("duration") is not None:
        print(f"Duration: {info['duration']} seconds")

    return video_path, info


# ============================================================
# FRAME EXTRACTION
# ============================================================

def extract_screenshots(video_path, output_folder, ffmpeg_path):
    """
    Extract a video frame every INTERVAL_SECONDS.

    Example:
        0.0 seconds
        3.5 seconds
        7.0 seconds
        10.5 seconds
        14.0 seconds
    """

    print("\n" + "=" * 65)
    print("EXTRACTING SCREENSHOTS")
    print("=" * 65)

    # Convert interval into an exact rational frame rate.
    # For 3.5 seconds:
    # 1 / 3.5 = 2 / 7 frames per second.
    interval = Fraction(str(INTERVAL_SECONDS))

    if interval <= 0:
        raise ValueError(
            "INTERVAL_SECONDS must be greater than zero."
        )

    output_fps = 1 / interval

    fps_expression = (
        f"{output_fps.numerator}/{output_fps.denominator}"
    )

    print(f"Interval: {INTERVAL_SECONDS} seconds")
    print(f"Extraction FPS: {fps_expression}")
    print("Image format: PNG")
    print("Image quality: Lossless")
    print("Resizing: Disabled")
    print("\nStarting FFmpeg extraction...\n")

    raw_output_pattern = str(
        output_folder / "raw_frame_%06d.png"
    )

    command = [
        ffmpeg_path,

        "-hide_banner",
        "-y",

        # Input video.
        "-i", str(video_path),

        # Process only the first video stream.
        "-map", "0:v:0",

        # Remove unnecessary streams.
        "-an",
        "-sn",
        "-dn",

        # Select one frame every configured interval.
        "-vf", f"fps={fps_expression}:start_time=0",

        # PNG compression.
        "-compression_level", PNG_COMPRESSION_LEVEL,

        # Frame numbering.
        "-start_number", "1",

        # Output filename pattern.
        raw_output_pattern
    ]

    subprocess.run(
        command,
        check=True
    )

    # Retrieve all generated frames in order.
    raw_frames = sorted(
        output_folder.glob("raw_frame_*.png")
    )

    if not raw_frames:
        raise RuntimeError(
            "FFmpeg did not generate any screenshots."
        )

    return raw_frames


# ============================================================
# FRAME RENAMING AND CSV MANIFEST
# ============================================================

def organize_screenshots(raw_frames, output_folder):
    """
    Rename extracted frames with their timestamps.

    Also generate a CSV manifest.
    """

    print("\n" + "=" * 65)
    print("ORGANIZING SCREENSHOTS")
    print("=" * 65)

    manifest_path = output_folder / "frames_manifest.csv"

    frame_records = []

    for index, raw_frame in enumerate(raw_frames):

        # First screenshot is at 0 seconds.
        timestamp_seconds = index * INTERVAL_SECONDS

        timestamp_ms = round(
            timestamp_seconds * 1000
        )

        timestamp_label = make_timestamp(
            timestamp_ms
        )

        frame_number = index + 1

        new_filename = (
            f"frame_{frame_number:06d}_"
            f"{timestamp_label}.png"
        )

        new_path = output_folder / new_filename

        raw_frame.rename(new_path)

        frame_records.append({
            "frame_number": frame_number,
            "timestamp_seconds": f"{timestamp_seconds:.3f}",
            "timestamp": timestamp_label,
            "filename": new_filename
        })

        if frame_number % 50 == 0:
            print(
                f"Organized {frame_number} screenshots..."
            )

    # Save CSV manifest.
    with open(
        manifest_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        fieldnames = [
            "frame_number",
            "timestamp_seconds",
            "timestamp",
            "filename"
        ]

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(frame_records)

    return frame_records


# ============================================================
# VIDEO METADATA
# ============================================================

def save_video_metadata(info, output_folder):

    metadata_path = output_folder / "video_metadata.txt"

    title = info.get("title", "Unknown")
    video_id = info.get("id", "Unknown")
    duration = info.get("duration", "Unknown")
    width = info.get("width", "Unknown")
    height = info.get("height", "Unknown")
    webpage_url = info.get("webpage_url", "Unknown")

    metadata = f"""
YOUTUBE SCREENSHOT EXTRACTION REPORT
====================================

Title: {title}
Video ID: {video_id}
Original URL: {webpage_url}

Duration: {duration} seconds
Original Width: {width}
Original Height: {height}

Screenshot Interval: {INTERVAL_SECONDS} seconds
Image Format: PNG
Image Compression: Lossless
Resizing: Disabled

Extraction Date:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    metadata_path.write_text(
        metadata.strip(),
        encoding="utf-8"
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print("\n")
    print("=" * 65)
    print("       YOUTUBE VIDEO SCREENSHOT EXTRACTOR")
    print("=" * 65)

    # Check FFmpeg.
    ffmpeg_path = get_ffmpeg_path()

    print(f"\nFFmpeg found: {ffmpeg_path}")

    # Ask for the only user input.
    youtube_url = input(
        "\nPaste YouTube video URL: "
    ).strip()

    if not youtube_url:
        print("ERROR: No URL provided.")
        return

    if not validate_youtube_url(youtube_url):
        print("ERROR: Please enter a valid YouTube URL.")
        return

    # Check output directory configuration.
    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    print(f"\nOutput root: {OUTPUT_ROOT}")
    print(f"Screenshot interval: {INTERVAL_SECONDS} seconds")

    try:

        # Temporary download directory.
        # This is automatically removed after processing.
        with tempfile.TemporaryDirectory(
            prefix="youtube_video_download_"
        ) as temporary_folder:

            # Step 1: Download the best available video.
            video_path, info = download_youtube_video(
                youtube_url,
                temporary_folder
            )

            # Step 2: Create a dedicated output folder.
            output_folder = create_output_folder(
                info.get("title", "youtube_video"),
                info.get("id", "unknown")
            )

            print(f"\nOutput folder created:\n{output_folder}")

            # Step 3: Extract frames.
            raw_frames = extract_screenshots(
                video_path,
                output_folder,
                ffmpeg_path
            )

            # Step 4: Rename images and create CSV.
            records = organize_screenshots(
                raw_frames,
                output_folder
            )

            # Step 5: Save video metadata.
            save_video_metadata(
                info,
                output_folder
            )

            total_frames = len(records)

        # The temporary video has now been removed.

        print("\n")
        print("=" * 65)
        print("             EXTRACTION COMPLETED!")
        print("=" * 65)

        print(f"\nTotal screenshots: {total_frames}")
        print(f"Interval: {INTERVAL_SECONDS} seconds")

        print("\nSaved files:")
        print(f"Output folder: {output_folder}")
        print(f"CSV manifest: {output_folder / 'frames_manifest.csv'}")
        print(f"Video metadata: {output_folder / 'video_metadata.txt'}")

        print("\nTemporary downloaded video has been deleted.")

        print("\n" + "=" * 65)

    except yt_dlp.utils.DownloadError as error:

        print("\nYOUTUBE DOWNLOAD ERROR:")
        print(error)

    except subprocess.CalledProcessError as error:

        print("\nFFMPEG EXTRACTION ERROR:")
        print(error)

    except KeyboardInterrupt:

        print("\nProcess interrupted by user.")

    except Exception as error:

        print("\nPIPELINE ERROR:")
        print(f"{type(error).__name__}: {error}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
