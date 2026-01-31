# Quizly Backend

A Django REST API that generates interactive quizzes from YouTube videos using Whisper AI for transcription and Google Gemini AI for quiz generation.

## Requirements

### System Requirements

- **Python 3.12 or higher** (tested with Python 3.14)
  - Django 6.0.1 requires at least Python 3.12
- **FFmpeg** (required for audio processing)

### FFmpeg Installation

FFmpeg is required by Whisper AI for audio transcription.

**Windows:**
```bash
winget install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### API Keys

- **Google Gemini API Key** (free tier available)
  - Get your key at: https://ai.google.dev/gemini-api/docs

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/BadRix90/quizly.git
cd quizly
```

### 2. Create Virtual Environment

**Important:** Use Python 3.12 or higher!

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the template and configure your environment variables:

```bash
# Windows (PowerShell):
copy .env.template .env

# macOS/Linux:
cp .env.template .env
```

**Edit `.env` and add your API key:**

```env
GEMINI_API_KEY=your_actual_api_key_here
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,[::1],.localhost
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

**Note:** If your frontend runs on a different port (e.g., 3000), update `CORS_ALLOWED_ORIGINS`:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 5. Database Setup

**CRITICAL:** Run both commands in order!

```bash
# Step 1: Create migration files
python manage.py makemigrations

# Step 2: Apply migrations to create database tables
python manage.py migrate
```

### 6. Create Superuser (Optional)

For admin panel access:

```bash
python manage.py createsuperuser
```

### 7. Start Server

```bash
python manage.py runserver
```

The backend will be available at: `http://localhost:8000`

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Django 6.0.1, DRF 3.16.1 | REST API Framework |
| Auth | djangorestframework-simplejwt | JWT with HTTP-only Cookies |
| YouTube | yt-dlp | Audio download from YouTube |
| Transcription | OpenAI Whisper | Local audio-to-text |
| Quiz Generation | Google Gemini 2.5 Flash | AI quiz creation |
| Audio Processing | FFmpeg | Required by Whisper |

## API Documentation

### Authentication

All endpoints use **JWT authentication with HTTP-only cookies**.

#### Register

**Endpoint:** `POST /api/register/`

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_password",
  "email": "your_email@example.com"
}
```

**Response:** `201 Created`
```json
{
  "detail": "User created successfully!"
}
```

#### Login

**Endpoint:** `POST /api/login/`

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Login successfully!",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

Sets `access_token` (30min) and `refresh_token` (24h) as HTTP-only cookies.

#### Logout

**Endpoint:** `POST /api/logout/`
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "detail": "Log-Out successfully! All Tokens will be deleted."
}
```

#### Refresh Token

**Endpoint:** `POST /api/token/refresh/`
**Authentication:** Required (refresh_token cookie)

**Response:** `200 OK`
```json
{
  "detail": "Token refreshed",
  "access": "new_access_token"
}
```

### Quiz Management

#### Create Quiz

**Endpoint:** `POST /api/createQuiz/`
**Authentication:** Required

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "Auto-generated Title",
  "description": "Auto-generated Description",
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "created_at": "2025-01-22T14:30:00Z",
  "questions": [
    {
      "id": 1,
      "question_title": "What is...?",
      "question_options": ["A", "B", "C", "D"],
      "answer": "A"
    }
  ]
}
```

#### List All Quizzes

**Endpoint:** `GET /api/quizzes/`
**Authentication:** Required

Returns all quizzes for the authenticated user.

#### Get Specific Quiz

**Endpoint:** `GET /api/quizzes/{id}/`
**Authentication:** Required

#### Update Quiz

**Endpoint:** `PATCH /api/quizzes/{id}/`
**Authentication:** Required

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated Description"
}
```

#### Delete Quiz

**Endpoint:** `DELETE /api/quizzes/{id}/`
**Authentication:** Required

**Response:** `204 No Content`

**Warning:** Deletion is permanent and cannot be undone!

## Project Structure

```
quizly/
├── quizly/                 # Django project settings
│   ├── settings.py        # Main configuration
│   └── urls.py            # Root URL routing
├── users/                 # User authentication app
│   ├── views.py          # Auth endpoints
│   ├── serializers.py    # Request/Response serialization
│   └── authentication.py # JWT cookie authentication
├── quizzes/              # Quiz management app
│   ├── views.py         # Quiz endpoints
│   ├── models.py        # Quiz, Question models
│   ├── serializers.py   # Quiz serialization
│   ├── services/        # Business logic
│   │   ├── youtube_service.py   # yt-dlp integration
│   │   └── gemini_service.py    # Gemini AI integration
│   └── utils/
│       └── quiz_generator.py    # Whisper transcription
├── .env                 # Environment variables (create from template)
├── .env.template       # Environment template
├── requirements.txt   # Python dependencies
└── manage.py         # Django management script
```

## Troubleshooting

### "Table does not exist" Error

You forgot to run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### "Invalid API Key" or Quota Error

Check that `GEMINI_API_KEY` in `.env` is set correctly. The free tier has rate limits.

### FFmpeg not found

Whisper requires FFmpeg for audio processing. Install it using the commands in the Requirements section.

### CORS Errors

Update `CORS_ALLOWED_ORIGINS` in `.env` to match your frontend URL.

### Python Version Error

Django 6.0.1 requires Python 3.12+. Check your version:
```bash
python --version
```

## Security Notes

- Never commit `.env` to version control
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use HTTPS in production
- Secure cookies are enabled automatically when `DEBUG=False`

## License

MIT

## Credits

- Frontend provided by [Developer Akademie](https://github.com/Developer-Akademie-Backendkurs/project.Quizly)
- Built with Django, OpenAI Whisper and Google Gemini AI
