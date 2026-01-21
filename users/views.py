"""Views for user authentication endpoints."""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    """Handle user registration via POST /api/register/."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate input and create new user, returns 201 or 400."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User created successfully!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Handle user login via POST /api/login/."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate user and set JWT cookies, returns 200 or 401."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        response = Response({
            "detail": "Login successfully!",
            "user": UserSerializer(user).data
        })

        self._set_auth_cookies(response, refresh)
        return response

    def _set_auth_cookies(self, response, refresh):
        """Set access_token and refresh_token as HTTP-only cookies."""
        jwt_settings = settings.SIMPLE_JWT

        response.set_cookie(
            key=jwt_settings.get('AUTH_COOKIE', 'access_token'),
            value=str(refresh.access_token),
            httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
            secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
            samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax'),
            path=jwt_settings.get('AUTH_COOKIE_PATH', '/')
        )
        response.set_cookie(
            key=jwt_settings.get('AUTH_COOKIE_REFRESH', 'refresh_token'),
            value=str(refresh),
            httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
            secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
            samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax'),
            path=jwt_settings.get('AUTH_COOKIE_PATH', '/')
        )


class LogoutView(APIView):
    """Handle user logout via POST /api/logout/."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist refresh token and delete auth cookies."""
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token')
        )

        if refresh_token:
            self._blacklist_token(refresh_token)

        response = Response({
            "detail": "Log-Out successfully! All Tokens will be deleted. "
                      "Refresh token is now invalid."
        })
        self._delete_auth_cookies(response)
        return response

    def _blacklist_token(self, token_str):
        """Add token to blacklist, silently ignore invalid tokens."""
        try:
            token = RefreshToken(token_str)
            token.blacklist()
        except TokenError:
            pass

    def _delete_auth_cookies(self, response):
        """Remove access_token and refresh_token cookies."""
        jwt_settings = settings.SIMPLE_JWT
        response.delete_cookie(
            jwt_settings.get('AUTH_COOKIE', 'access_token'),
            path=jwt_settings.get('AUTH_COOKIE_PATH', '/')
        )
        response.delete_cookie(
            jwt_settings.get('AUTH_COOKIE_REFRESH', 'refresh_token'),
            path=jwt_settings.get('AUTH_COOKIE_PATH', '/')
        )


class TokenRefreshView(APIView):
    """Handle token refresh via POST /api/token/refresh/."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Generate new access token from refresh token cookie."""
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token')
        )

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response({
            "detail": "Token refreshed",
            "access": new_access
        })
        self._set_access_cookie(response, new_access)
        return response

    def _set_access_cookie(self, response, access_token):
        """Set new access_token cookie."""
        jwt_settings = settings.SIMPLE_JWT
        response.set_cookie(
            key=jwt_settings.get('AUTH_COOKIE', 'access_token'),
            value=access_token,
            httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
            secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
            samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax'),
            path=jwt_settings.get('AUTH_COOKIE_PATH', '/')
        )