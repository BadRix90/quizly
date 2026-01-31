"""Views for quiz management according to endpoint.md."""

import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Quiz, Question
from .serializers import (
    QuizSerializer,
    QuizUpdateSerializer,
    CreateQuizSerializer
)
from .services import download_audio, transcribe_audio, generate_quiz


class CreateQuizView(APIView):
    """POST /api/createQuiz/ - Create quiz from YouTube URL."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create new quiz from YouTube video."""
        serializer = CreateQuizSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        url = serializer.validated_data['url']
        try:
            quiz = self._create_quiz_from_url(url, request.user)
            return Response(
                QuizSerializer(quiz).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _create_quiz_from_url(self, url: str, user):
        """Pipeline: Download -> Transcribe -> Generate Quiz."""
        audio_path = download_audio(url)
        transcript = transcribe_audio(audio_path)
        quiz_data = generate_quiz(transcript)
        quiz = self._save_quiz(quiz_data, url, user)
        self._cleanup_audio(audio_path)
        return quiz

    def _save_quiz(self, quiz_data: dict, url: str, user):
        """Save quiz and questions to database."""
        quiz = Quiz.objects.create(
            title=quiz_data['title'],
            description=quiz_data['description'],
            video_url=url,
            user=user
        )
        self._save_questions(quiz, quiz_data['questions'])
        return quiz

    def _save_questions(self, quiz, questions: list):
        """Save questions for quiz."""
        for q in questions:
            Question.objects.create(
                quiz=quiz,
                question_title=q['question_title'],
                question_options=q['question_options'],
                answer=q['answer']
            )

    def _cleanup_audio(self, audio_path: str):
        """Delete temporary audio file."""
        if os.path.exists(audio_path):
            os.remove(audio_path)


class QuizListView(APIView):
    """GET /api/quizzes/ - List all quizzes for authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all quizzes for current user."""
        quizzes = Quiz.objects.filter(user=request.user)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)


class QuizDetailView(APIView):
    """GET/PATCH/DELETE /api/quizzes/{id}/ - Single quiz operations."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Return single quiz."""
        quiz = self._get_user_quiz(pk, request.user)
        return Response(QuizSerializer(quiz).data)

    def patch(self, request, pk):
        """Update quiz title and description."""
        quiz = self._get_user_quiz(pk, request.user)
        serializer = QuizUpdateSerializer(
            quiz,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(QuizSerializer(quiz).data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        """Delete quiz permanently."""
        quiz = self._get_user_quiz(pk, request.user)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_user_quiz(self, pk, user):
        """Get quiz and verify ownership."""
        quiz = get_object_or_404(Quiz, pk=pk)
        if quiz.user != user:
            raise PermissionDenied("Quiz does not belong to user.")
        return quiz