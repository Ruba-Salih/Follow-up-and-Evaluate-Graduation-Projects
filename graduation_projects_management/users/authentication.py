from rest_framework.authentication import SessionAuthentication

class CSRFExemptSessionAuthentication(SessionAuthentication):
    """
    Custom authentication class that disables CSRF checks for API requests.
    """
    def enforce_csrf(self, request):
        return  # ✅ This disables CSRF checks for API requests
