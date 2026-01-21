"""
Custom JWT Authentication for HTTP-Only Cookies.

Reads JWT token from cookies instead of Authorization header.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication that reads token from HTTP-Only cookies.
    
    Uses 'access_token' cookie instead of Authorization header.
    """

    def authenticate(self, request):
        """
        Authenticate request using access_token cookie.
        
        Returns:
            Tuple (user, validated_token) or None
        """
        raw_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token')
        )
        
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token