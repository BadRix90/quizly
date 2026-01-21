"""
Serializers für User Authentication.

Endpoints:
- POST /api/register/
- POST /api/login/
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.Serializer):
    """
    Serializer für Benutzerregistrierung.
    
    Request Body:
        username, password, confirmed_password, email
    """

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        """Prüft ob Username bereits existiert."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return value

    def validate_email(self, value):
        """Prüft ob Email bereits existiert."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return value

    def validate(self, data):
        """Prüft ob Passwörter übereinstimmen."""
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError(
                {"confirmed_password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        """Erstellt neuen User."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer für Benutzeranmeldung.
    
    Request Body:
        username, password
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authentifiziert User mit Credentials."""
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        if user is None:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer für User Response."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']