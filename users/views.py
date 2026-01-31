"""Views for user authentication endpoints."""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


def _get_cookie_settings():
    """Return JWT cookie configuration from settings."""
    jwt = settings.SIMPLE_JWT
    return {
        'httponly': jwt.get('AUTH_COOKIE_HTTP_ONLY', True),
        'secure': jwt.get('AUTH_COOKIE_SECURE', False),
        'samesite': jwt.get('AUTH_COOKIE_SAMESITE', 'Lax'),
        'path': jwt.get('AUTH_COOKIE_PATH', '/')
    }


def _set_cookie(response, key, value):
    """Set a single HTTP-only cookie with JWT settings."""
    opts = _get_cookie_settings()
    response.set_cookie(key=key, value=value, **opts)


def _get_cookie_name(key):
    """Get cookie name from settings with fallback."""
    defaults = {'access': 'access_token', 'refresh': 'refresh_token'}
    setting_keys = {'access': 'AUTH_COOKIE', 'refresh': 'AUTH_COOKIE_REFRESH'}
    return settings.SIMPLE_JWT.get(setting_keys[key], defaults[key])


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
        _set_cookie(response, _get_cookie_name('access'), str(refresh.access_token))
        _set_cookie(response, _get_cookie_name('refresh'), str(refresh))
        return response


class LogoutView(APIView):
    """Handle user logout via POST /api/logout/."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist refresh token and delete auth cookies."""
        refresh_token = request.COOKIES.get(_get_cookie_name('refresh'))
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
            RefreshToken(token_str).blacklist()
        except TokenError:
            pass

    def _delete_auth_cookies(self, response):
        """Remove access_token and refresh_token cookies."""
        path = _get_cookie_settings()['path']
        response.delete_cookie(_get_cookie_name('access'), path=path)
        response.delete_cookie(_get_cookie_name('refresh'), path=path)


class TokenRefreshView(APIView):
    """Handle token refresh via POST /api/token/refresh/."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Generate new access token from refresh token cookie."""
        refresh_token = request.COOKIES.get(_get_cookie_name('refresh'))
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
        response = Response({"detail": "Token refreshed", "access": new_access})
        _set_cookie(response, _get_cookie_name('access'), new_access)
        return response
