"""YouTube audio download service using yt-dlp. Requires FFMPEG globally installed."""

import os
import yt_dlp
from django.conf import settings


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url


def download_audio(url: str) -> str:
    """Download audio from YouTube video and return file path."""
    video_id = extract_video_id(url)
    output_path = settings.AUDIO_OUTPUT_PATH
    os.makedirs(output_path, exist_ok=True)

    tmp_filename = os.path.join(output_path, f"{video_id}.%(ext)s")
    ydl_opts = _get_download_options(tmp_filename)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def _get_download_options(output_template: str) -> dict:
    """Create yt-dlp configuration options."""
    return {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True,
    }