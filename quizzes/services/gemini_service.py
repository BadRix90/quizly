"""Gemini AI Quiz Generation Service using python-genai SDK."""

import re
import json
from google import genai
from django.conf import settings


def generate_quiz(transcript: str) -> dict:
    """
    Generate quiz questions from transcript using Gemini 2.5 Flash.

    Args:
        transcript: Text content to generate questions from.

    Returns:
        Dictionary with title, description and list of questions.

    Raises:
        ValueError: If GEMINI_API_KEY is not configured.
        JSONDecodeError: If response is not valid JSON.
    """
    client = _get_gemini_client()
    prompt = _build_quiz_prompt(transcript)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return _parse_quiz_response(response.text)


def _get_gemini_client():
    """
    Create Gemini API client with configured API key.

    Returns:
        genai.Client instance ready for API calls.

    Raises:
        ValueError: If GEMINI_API_KEY is not set in settings.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY not configured.")
    return genai.Client(api_key=api_key)


def _build_quiz_prompt(transcript: str) -> str:
    """
    Build the prompt for quiz generation.

    Args:
        transcript: The video transcript text.

    Returns:
        Formatted prompt string for Gemini API.
    """
    return f"""Based on the following transcript, generate a quiz in valid JSON format.
The quiz must follow this exact structure:
{{
  "title": "Create a concise quiz title based on the topic.",
  "description": "Summarize the transcript in max 150 characters.",
  "questions": [
    {{
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the options"
    }}
  ]
}}
Requirements:
- Exactly 10 questions with 4 options each.
- Only valid JSON, no explanations.

Transcript:
{transcript}
"""


def _parse_quiz_response(text: str) -> dict:
    """
    Clean and parse JSON response from Gemini.

    Args:
        text: Raw response text from Gemini API.

    Returns:
        Parsed dictionary with quiz data.

    Raises:
        JSONDecodeError: If cleaned text is not valid JSON.
    """
    cleaned = re.sub(r'^```json\s*', '', text.strip())
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    return json.loads(cleaned.strip())
