from datetime import datetime
from django.utils.timezone import now


class UpdateLastConnectionMiddleware:
    """
    Middleware to update the `last_connection` field for authenticated users.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Update last_connection only for authenticated users
        if request.user.is_authenticated:
            request.user.last_connection = now()
            request.user.save(update_fields=['last_connection'])

        response = self.get_response(request)
        return response
