"""Custom middleware to prevent caching of authenticated pages."""


class NoCacheMiddleware:
    """
    Middleware that adds Cache-Control headers to prevent browser caching.
    
    This ensures that after logout, users cannot use browser back button
    to view cached protected pages. The frontend's checkAuth() will execute
    immediately on page load, resulting in proper 401 redirects.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Apply no-cache headers to all API endpoints
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response