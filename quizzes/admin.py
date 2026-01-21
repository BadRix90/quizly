"""
Admin Konfiguration für Quiz und Question.

Ermöglicht Bearbeitung von Quizzes und Fragen im Admin Panel.
"""

from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.TabularInline):
    """Inline-Editor für Questions innerhalb Quiz."""

    model = Question
    extra = 0
    fields = ['question_title', 'question_options', 'answer']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin für Quiz Model."""

    list_display = ['title', 'user', 'created_at', 'updated_at']
    list_filter = ['user', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin für Question Model."""

    list_display = ['question_title_short', 'quiz', 'answer']
    list_filter = ['quiz']
    search_fields = ['question_title', 'answer']

    def question_title_short(self, obj):
        """Zeigt gekürzte Frage an."""
        return obj.question_title[:50] + "..." if len(obj.question_title) > 50 else obj.question_title
    question_title_short.short_description = 'Question'