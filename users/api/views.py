from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


def _set_auth_cookie(response, key, value):
    """Set JWT token as HTTP-only cookie."""
    jwt_settings = settings.SIMPLE_JWT
    response.set_cookie(
        key=key,
        value=value,
        httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
        secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
        samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax'),
        path=jwt_settings.get('AUTH_COOKIE_PATH', '/')
    )


def _delete_auth_cookie(response, key):
    """Delete JWT cookie by setting it to empty with immediate expiry."""
    jwt_settings = settings.SIMPLE_JWT
    response.set_cookie(
        key=key,
        value='',
        max_age=0,
        expires='Thu, 01 Jan 1970 00:00:00 GMT',
        path=jwt_settings.get('AUTH_COOKIE_PATH', '/'),
        secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
        httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
        samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax')
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User created successfully!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        response = Response({
            "detail": "Login successful!",
            "user": UserSerializer(user).data
        })

        _set_auth_cookie(response, 'access_token', str(refresh.access_token))
        _set_auth_cookie(response, 'refresh_token', str(refresh))

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        response = Response({"detail": "Logout successful."})

        _delete_auth_cookie(response, 'access_token')
        _delete_auth_cookie(response, 'refresh_token')

        return response


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            new_access = str(RefreshToken(refresh_token).access_token)
        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response({"detail": "Token refreshed."})
        _set_auth_cookie(response, 'access_token', new_access)

        return response
