import yt_dlp
import whisper
from google import genai
import os
import json
import re

GEMINI_API_KEY = "AIzaSyCYaLQIus6CqFQc0Vna80LjToeeflGIxOM"
client = genai.Client(api_key=GEMINI_API_KEY)

def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url

def download_audio(url: str, output_path: str = "audio") -> str:
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
        print(f"✅ Audio heruntergeladen: {filename}")
        return filename

def transcribe_audio(audio_path: str, model_name: str = "base") -> str:
    print(f"🔄 Lade Whisper-Modell '{model_name}'...")
    model = whisper.load_model(model_name)
    
    print("🔄 Transkribiere Audio...")
    result = model.transcribe(audio_path)
    
    print("✅ Transkription abgeschlossen!")
    return result["text"]

def clean_json_response(text: str) -> str:
    text = re.sub(r'^```json\s*', '', text.strip())
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()

def generate_quiz(transcript: str) -> dict:
    print("🔄 Generiere Quiz mit Gemini...")
    
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
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    cleaned_text = clean_json_response(response.text)
    quiz = json.loads(cleaned_text)
    
    print(f"✅ Quiz '{quiz['title']}' mit {len(quiz['questions'])} Fragen generiert!")
    return quiz

def run_quiz(quiz: dict):
    print("\n" + "="*50)
    print(f"🎯 {quiz['title']}")
    print(f"📝 {quiz['description']}")
    print("="*50 + "\n")
    
    score = 0
    questions = quiz['questions']
    
    for i, q in enumerate(questions, 1):
        print(f"Frage {i}: {q['question_title']}\n")
        for j, option in enumerate(q['question_options']):
            print(f"  {j + 1}. {option}")
        
        while True:
            try:
                answer = int(input("\nDeine Antwort (1-4): ")) - 1
                if 0 <= answer <= 3:
                    break
            except ValueError:
                pass
            print("Bitte 1-4 eingeben!")
        
        selected_answer = q['question_options'][answer]
        if selected_answer == q['answer']:
            print("✅ Richtig!\n")
            score += 1
        else:
            print(f"❌ Falsch! Richtig war: {q['answer']}\n")
    
    print("="*50)
    print(f"🏆 Ergebnis: {score}/{len(questions)} Punkten")
    print("="*50)

if __name__ == "__main__":
    url = input("YouTube-URL eingeben: ")
    
    audio_file = download_audio(url)
    transcript = transcribe_audio(audio_file)
    
    print("\n📝 Transkription:\n")
    print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
    
    quiz = generate_quiz(transcript)
    run_quiz(quiz)