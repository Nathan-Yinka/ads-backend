from rest_framework.response import Response
from rest_framework import status


class StandardResponseMixin:
    """
    Mixin to wrap all responses in the standard response format.
    """

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Override finalize_response to format responses in the standard format.
        """
        # Check if the response is an instance of DRF's Response and has data
        if isinstance(response, Response) and isinstance(response.data, dict):
            success = 200 <= response.status_code < 300
            message = response.data.pop('message', "Success" if success else "Error")
            data = response.data if success else {}
            errors = None if success else response.data

            response.data = {
                "success": success,
                "message": message,
                "data": data,
                "errors": errors
            }
        return super().finalize_response(request, response, *args, **kwargs)
