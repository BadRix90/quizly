# Quizly Backend

A Django REST API that generates interactive quizzes from YouTube videos using Google Gemini AI.

## 📋 Requirements

### System Requirements

- **Python 3.12 or higher** (tested with Python 3.14)
  - **IMPORTANT:** Django 6.0.1 requires at least Python 3.12

### API Keys

- **Google Gemini API Key** (free tier available)
  - Get your key at: https://ai.google.dev/gemini-api/docs

## 🚀 Installation

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

## 📚 API Documentation

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

**⚠️ Warning:** Deletion is permanent and cannot be undone!

## 🏗️ Project Structure

```
quizly/
├── quizly/                 # Django project settings
│   ├── settings.py        # Main configuration
│   └── urls.py            # Root URL routing
├── users/                 # User authentication app
│   ├── api/              # API endpoints
│   ├── migrations/       # Database migrations
│   └── authentication.py # JWT cookie authentication
├── quizzes/              # Quiz management app
│   ├── api/             # API endpoints
│   ├── migrations/      # Database migrations
│   └── utils/           # Helper functions
│       └── quiz_generator.py  # YouTube → Quiz pipeline
├── .env                 # Environment variables (create from template)
├── .env.template       # Environment template
├── .gitignore         # Git ignore rules
├── requirements.txt   # Python dependencies (lowercase!)
└── manage.py         # Django management script
```

## 🔍 Troubleshooting

### "Table does not exist" Error

You forgot to run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### "Invalid API Key"

Check that `GEMINI_API_KEY` in `.env` is set correctly.

### CORS Errors

Update `CORS_ALLOWED_ORIGINS` in `.env` to match your frontend URL.

### Python Version Error

Django 6.0.1 requires Python 3.12+. Check your version:
```bash
python --version
```

## 🔒 Security Notes

- Never commit `.env` to version control
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use HTTPS in production
- Secure cookies are enabled automatically when `DEBUG=False`

## 📦 Tech Stack

- Django 6.0.1
- Django REST Framework 3.16.1
- djangorestframework-simplejwt 5.5.0
- python-decouple 3.8
- yt-dlp 2025.01.26
- google-generativeai 0.8.3

## 📝 License

MIT

## 👥 Credits

- Frontend provided by [Developer Akademie](https://github.com/Developer-Akademie-Backendkurs/project.Quizly)
- Built with Django and Google Gemini AI