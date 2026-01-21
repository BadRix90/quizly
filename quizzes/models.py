"""
Models für Quiz und Question.

Struktur gemäß endpoint.md Response:
- Quiz: id, title, description, video_url, created_at, updated_at, user
- Question: id, question_title, question_options, answer, created_at, updated_at
"""

from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    """
    Quiz Model.
    
    Speichert Quiz-Metadaten und Referenz zum YouTube Video.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quizzes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Question Model.
    
    Speichert einzelne Quizfragen mit Optionen und Antwort.
    question_options wird als JSON-Array gespeichert.
    """

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_title = models.TextField()
    question_options = models.JSONField(default=list)
    answer = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['id']

    def __str__(self):
        return f"{self.quiz.title} - {self.question_title[:50]}"