"""
Whisper AI Transkription Service.

Verwendet OpenAI Whisper für Audio-zu-Text Konvertierung.
Benötigt: FFMPEG global installiert!
"""

import whisper
from django.conf import settings


def transcribe_audio(audio_path: str) -> str:
    """
    Transkribiert Audio-Datei mit Whisper AI.
    
    Args:
        audio_path: Pfad zur Audio-Datei
        
    Returns:
        Transkribierter Text
    """
    model_name = getattr(settings, 'WHISPER_MODEL', 'base')
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    return result["text"]