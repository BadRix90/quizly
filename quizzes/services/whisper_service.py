"""Whisper AI transcription service. Requires FFMPEG globally installed."""

import whisper
from django.conf import settings


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Whisper AI."""
    model_name = getattr(settings, 'WHISPER_MODEL', 'base')
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    return result["text"]