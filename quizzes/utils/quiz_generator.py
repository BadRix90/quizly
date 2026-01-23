"""YouTube to Quiz Generator using only Gemini (no Whisper, no FFmpeg)."""

import os
import re
import json
import yt_dlp
from google import genai
from decouple import config

GEMINI_API_KEY = config('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env!")

client = genai.Client(api_key=GEMINI_API_KEY)


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url


def download_audio(url: str, output_path: str = "audio") -> str:
    """Download audio from YouTube video."""
    video_id = extract_video_id(url)
    normalized_url = f"https://www.youtube.com/watch?v={video_id}"
    tmp_filename = os.path.join(output_path, f"{video_id}.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
    }
    
    os.makedirs(output_path, exist_ok=True)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(normalized_url, download=True)
        filename = ydl.prepare_filename(info)
        print(f"✅ Audio downloaded: {filename}")
        return filename


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using Gemini File API."""
    print("🔄 Uploading audio to Gemini...")
    uploaded_file = client.files.upload(file=audio_path)
    
    print("🔄 Transcribing audio with Gemini...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[
            uploaded_file,
            "Transcribe this audio file. Provide only the transcript text, no explanations."
        ]
    )
    
    print("✅ Transcription completed!")
    return response.text


def clean_json_response(text: str) -> str:
    """Remove markdown formatting from JSON response."""
    text = re.sub(r'^```json\s*', '', text.strip())
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


def generate_quiz(transcript: str) -> dict:
    """Generate quiz from transcript using Gemini."""
    print("🔄 Generating quiz with Gemini...")
    
    prompt = f"""Based on the following transcript, generate a quiz in valid JSON format.
The quiz must follow this exact structure:
{{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {{
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    }},
    ...
    (exactly 10 questions)
  ]
}}
Requirements:
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON.

Transcript:
{transcript}
"""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    
    cleaned_text = clean_json_response(response.text)
    quiz = json.loads(cleaned_text)
    
    print(f"✅ Quiz '{quiz['title']}' with {len(quiz['questions'])} questions generated!")
    return quiz


def run_quiz(quiz: dict):
    """Run quiz interactively in console."""
    print("\n" + "="*50)
    print(f"🎯 {quiz['title']}")
    print(f"📝 {quiz['description']}")
    print("="*50 + "\n")
    
    score = 0
    questions = quiz['questions']
    
    for i, q in enumerate(questions, 1):
        print(f"Question {i}: {q['question_title']}\n")
        for j, option in enumerate(q['question_options']):
            print(f"  {j + 1}. {option}")
        
        while True:
            try:
                answer = int(input("\nYour answer (1-4): ")) - 1
                if 0 <= answer <= 3:
                    break
            except ValueError:
                pass
            print("Please enter 1-4!")
        
        selected_answer = q['question_options'][answer]
        if selected_answer == q['answer']:
            print("✅ Correct!\n")
            score += 1
        else:
            print(f"❌ Wrong! Correct answer: {q['answer']}\n")
    
    print("="*50)
    print(f"🏆 Result: {score}/{len(questions)} points")
    print("="*50)


if __name__ == "__main__":
    url = input("Enter YouTube URL: ")
    
    audio_file = download_audio(url)
    transcript = transcribe_audio(audio_file)
    
    print("\n📝 Transcript:\n")
    print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
    
    quiz = generate_quiz(transcript)
    run_quiz(quiz)