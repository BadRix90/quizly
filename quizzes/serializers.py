"""Quiz and Question serializers matching endpoint.md response structure."""

from rest_framework import serializers
from .models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""

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
    """Serializer for Quiz model with nested questions."""

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
    """Serializer for PATCH /api/quizzes/{id}/."""

    class Meta:
        model = Quiz
        fields = ['title', 'description']


class CreateQuizSerializer(serializers.Serializer):
    """Serializer for POST /api/createQuiz/."""

    url = serializers.URLField()

    def validate_url(self, value):
        """Validate YouTube URL."""
        if 'youtube.com' not in value and 'youtu.be' not in value:
            raise serializers.ValidationError(
                "URL must be a valid YouTube URL."
            )
        return value