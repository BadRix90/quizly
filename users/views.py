"""
Views für User Authentication.

Endpoints gemäß endpoint.md:
- POST /api/register/ - Registrierung
- POST /api/login/ - Anmeldung mit Cookie-Setting
- POST /api/logout/ - Abmeldung mit Token-Blacklist
- POST /api/token/refresh/ - Token erneuern
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    """
    POST /api/register/
    
    Registriert einen neuen Benutzer.
    Status Codes: 201, 400, 500
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Erstellt neuen Benutzer nach Validierung."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User created successfully!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/login/
    
    Meldet Benutzer an und setzt Auth-Cookies.
    Status Codes: 200, 401, 500
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Authentifiziert User und setzt JWT Cookies."""
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
        """Setzt access_token und refresh_token Cookies."""
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
    """
    POST /api/logout/
    
    Meldet Benutzer ab und invalidiert Tokens.
    Status Codes: 200, 401, 500
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklistet Refresh Token und löscht Cookies."""
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
        """Fügt Token zur Blacklist hinzu."""
        try:
            token = RefreshToken(token_str)
            token.blacklist()
        except TokenError:
            pass

    def _delete_auth_cookies(self, response):
        """Löscht Auth Cookies."""
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
    """
    POST /api/token/refresh/
    
    Erneuert Access-Token mittels Refresh-Token.
    Status Codes: 200, 401, 500
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Erstellt neuen Access Token aus Refresh Token."""
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
        """Setzt neuen access_token Cookie."""
        jwt_settings = settings.SIMPLE_JWT
        response.set_cookie(
            key=jwt_settings.get('AUTH_COOKIE', 'access_token'),
            value=access_token,
            httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
            secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
            samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax'),
            path=jwt_settings.get('AUTH_COOKIE_PATH', '/')
        )