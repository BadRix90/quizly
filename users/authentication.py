"""Custom JWT authentication reading tokens from HTTP-Only cookies."""

from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """JWT authentication using access_token cookie instead of Authorization header."""

    def authenticate(self, request):
        """Authenticate request using access_token cookie, returns (user, token) or None."""
        raw_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token')
        )
        
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token