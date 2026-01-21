"""
Serializers für Quiz und Question.

Response-Struktur exakt wie in endpoint.md definiert.
"""

from rest_framework import serializers
from .models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer für Question Model."""

    class Meta:
        model = Question
        fields = [
            'id',
            'question_title',
            'question_options',
            'answer',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer für Quiz Model.
    
    Inkludiert verschachtelte Questions.
    """

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuizUpdateSerializer(serializers.ModelSerializer):
    """Serializer für PATCH /api/quizzes/{id}/."""

    class Meta:
        model = Quiz
        fields = ['title', 'description']


class CreateQuizSerializer(serializers.Serializer):
    """Serializer für POST /api/createQuiz/."""

    url = serializers.URLField()

    def validate_url(self, value):
        """Validiert YouTube URL."""
        if 'youtube.com' not in value and 'youtu.be' not in value:
            raise serializers.ValidationError(
                "URL must be a valid YouTube URL."
            )
        return value