# quizzes/utils/quiz_generator.py
"""Audio transcription utilities using Whisper AI."""

import whisper


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file using local Whisper model.

    Args:
        audio_path: Absolute path to audio file.

    Returns:
        Transcribed text as string.

    Raises:
        FileNotFoundError: If audio file does not exist.
        RuntimeError: If transcription fails.
    """
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language="de")
    return result["text"]
