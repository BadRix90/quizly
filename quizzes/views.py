"""
Views für Quiz Management.

Endpoints gemäß endpoint.md:
- POST /api/createQuiz/ - Quiz aus YouTube URL erstellen
- GET /api/quizzes/ - Alle Quizzes des Users
- GET /api/quizzes/{id}/ - Einzelnes Quiz
- PATCH /api/quizzes/{id}/ - Quiz aktualisieren
- DELETE /api/quizzes/{id}/ - Quiz löschen
"""

import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Quiz, Question
from .serializers import (
    QuizSerializer,
    QuizUpdateSerializer,
    CreateQuizSerializer
)
from .services import download_audio, transcribe_audio, generate_quiz


class CreateQuizView(APIView):
    """
    POST /api/createQuiz/
    
    Erstellt Quiz aus YouTube URL.
    Status Codes: 201, 400, 401, 500
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Erstellt neues Quiz aus YouTube Video."""
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
        """Pipeline: Download -> Transkript -> Quiz."""
        audio_path = download_audio(url)
        transcript = transcribe_audio(audio_path)
        quiz_data = generate_quiz(transcript)
        quiz = self._save_quiz(quiz_data, url, user)
        self._cleanup_audio(audio_path)
        return quiz

    def _save_quiz(self, quiz_data: dict, url: str, user):
        """Speichert Quiz und Questions in DB."""
        quiz = Quiz.objects.create(
            title=quiz_data['title'],
            description=quiz_data['description'],
            video_url=url,
            user=user
        )
        self._save_questions(quiz, quiz_data['questions'])
        return quiz

    def _save_questions(self, quiz, questions: list):
        """Speichert Questions für Quiz."""
        for q in questions:
            Question.objects.create(
                quiz=quiz,
                question_title=q['question_title'],
                question_options=q['question_options'],
                answer=q['answer']
            )

    def _cleanup_audio(self, audio_path: str):
        """Löscht temporäre Audio-Datei."""
        if os.path.exists(audio_path):
            os.remove(audio_path)


class QuizListView(APIView):
    """
    GET /api/quizzes/
    
    Listet alle Quizzes des authentifizierten Users.
    Status Codes: 200, 401, 500
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Gibt alle Quizzes des Users zurück."""
        quizzes = Quiz.objects.filter(user=request.user)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)


class QuizDetailView(APIView):
    """
    GET/PATCH/DELETE /api/quizzes/{id}/
    
    Einzelnes Quiz abrufen, aktualisieren oder löschen.
    Status Codes: 200, 204, 400, 401, 403, 404, 500
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Gibt einzelnes Quiz zurück."""
        quiz = self._get_user_quiz(pk, request.user)
        return Response(QuizSerializer(quiz).data)

    def patch(self, request, pk):
        """Aktualisiert Quiz (title, description)."""
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
        """Löscht Quiz permanent."""
        quiz = self._get_user_quiz(pk, request.user)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_user_quiz(self, pk, user):
        """Holt Quiz und prüft Ownership."""
        quiz = get_object_or_404(Quiz, pk=pk)
        if quiz.user != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Quiz gehört nicht dem Benutzer.")
        return quiz