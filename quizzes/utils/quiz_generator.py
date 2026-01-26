# quizzes/utils/quiz_generator.py
"""Quiz generation utilities using Whisper and Gemini."""

import json
import whisper
from google import generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


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


def generate_quiz(transcript: str) -> dict:
    """
    Generate quiz questions from transcript using Gemini 2.5 Flash.
    
    Args:
        transcript: Text content to generate questions from.
        
    Returns:
        Dictionary containing quiz title and list of questions.
        Structure: {
            "title": str,
            "questions": [{
                "question": str,
                "options": list[str],
                "correct_answer": int
            }]
        }
        
    Raises:
        JSONDecodeError: If Gemini response is not valid JSON.
        ValueError: If response structure is invalid.
    """
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
Create a quiz with 10 multiple-choice questions based on this transcript:

{transcript}

Respond ONLY with valid JSON in this format:
{{
  "title": "Quiz Title",
  "questions": [
    {{
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0
    }}
  ]
}}
"""
    
    response = model.generate_content(
        prompt,
        generation_config={
            "response_mime_type": "application/json"
        }
    )
    
    return json.loads(response.text)