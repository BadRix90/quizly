"""
YouTube Audio Download Service.

Verwendet yt-dlp zum Herunterladen von Audio aus YouTube Videos.
Benötigt: FFMPEG global installiert!
"""

import os
import yt_dlp
from django.conf import settings


def extract_video_id(url: str) -> str:
    """
    Extrahiert Video-ID aus YouTube URL.
    
    Args:
        url: YouTube URL (verschiedene Formate)
        
    Returns:
        Video-ID als String
    """
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url


def download_audio(url: str) -> str:
    """
    Lädt Audio von YouTube Video herunter.
    
    Args:
        url: YouTube Video URL
        
    Returns:
        Pfad zur Audio-Datei
        
    Raises:
        Exception: Bei Download-Fehler
    """
    video_id = extract_video_id(url)
    output_path = settings.AUDIO_OUTPUT_PATH
    os.makedirs(output_path, exist_ok=True)

    tmp_filename = os.path.join(output_path, f"{video_id}.%(ext)s")
    ydl_opts = _get_download_options(tmp_filename)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def _get_download_options(output_template: str) -> dict:
    """Erstellt yt-dlp Konfiguration."""
    return {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True,
    }