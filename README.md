# Quizly Backend

A Django REST API that generates quizzes from YouTube videos using AI.

## Features

- User authentication with JWT (HTTP-Only Cookies)
- YouTube video to audio conversion
- Audio transcription with Whisper AI
- Quiz generation with Google Gemini Flash
- Full CRUD operations for quizzes

## Prerequisites

- Python 3.10+
- **FFMPEG** (globally installed!)
- Gemini API Key

### Install FFMPEG

**Windows:**
```bash
winget install FFmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/BadRix90/quizly.git
cd quizly
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` with your values:
```
GEMINI_API_KEY=your-gemini-api-key
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Create superuser (optional):
```bash
python manage.py createsuperuser
```

8. Start server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Register new user |
| POST | `/api/login/` | Login and set cookies |
| POST | `/api/logout/` | Logout and invalidate tokens |
| POST | `/api/token/refresh/` | Refresh access token |

### Quiz Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/createQuiz/` | Create quiz from YouTube URL |
| GET | `/api/quizzes/` | List all user quizzes |
| GET | `/api/quizzes/{id}/` | Get single quiz |
| PATCH | `/api/quizzes/{id}/` | Update quiz title/description |
| DELETE | `/api/quizzes/{id}/` | Delete quiz |

## Tech Stack

- Django 6.0.1
- Django REST Framework 3.16.1
- djangorestframework-simplejwt 5.5.0
- yt-dlp 2025.01.26
- openai-whisper 20250625
- google-genai 1.59.0

## License

MIT