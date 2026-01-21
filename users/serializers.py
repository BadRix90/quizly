"""Serializers for user authentication endpoints."""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration with username, email and password."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        """Validate that username does not already exist."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return value

    def validate_email(self, value):
        """Validate that email does not already exist."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return value

    def validate(self, data):
        """Validate that password and confirmed_password match."""
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError(
                {"confirmed_password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        """Create and return a new user instance."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with username and password."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate user and attach user object to validated data."""
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
    """Serializer for user response data."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']