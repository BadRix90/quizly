"""
URL configuration for quizly project.

All API routes under /api/ according to endpoint.md:
- /api/register/
- /api/login/
- /api/logout/
- /api/token/refresh/
- /api/createQuiz/
- /api/quizzes/
- /api/quizzes/{id}/
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('quizzes.urls')),
]