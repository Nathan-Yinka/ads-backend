from rest_framework.response import Response
from shared.utils import standard_response


class StandardResponseMixin:
    """
    Mixin to wrap all responses in the standard response format.
    """

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Override finalize_response to ensure proper renderer handling and avoid double wrapping.
        """
        if isinstance(response, Response) and hasattr(response, 'data'):
            # Check if the response is already in the standard format
            if (
                isinstance(response.data, dict) and
                "success" in response.data and
                "message" in response.data and
                "data" in response.data
            ):
                return super().finalize_response(request, response, *args, **kwargs)

            # Safely handle response data based on type
            success = 200 <= response.status_code < 300
            message = (
                response.data.get('message')
                if isinstance(response.data, dict) and 'message' in response.data
                else ("Success" if success else "An error occurred")
            )

            # Handle response.data as a list or dict
            if isinstance(response.data, list):
                data = response.data if success else {}
                errors = None if success else response.data
            elif isinstance(response.data, dict):
                data = response.data if success else {}
                errors = None if success else response.data
            else:
                data = response.data  # Handle unexpected formats gracefully
                errors = None if success else {"detail": "Unexpected response format."}

            # Wrap the response in the standard format
            response.data = {
                "success": success,
                "message": message,
                "data": data,
                "errors": errors,
            }

            # Ensure the response has the request context
            response.accepted_renderer = self.renderer_classes[0]()
            response.accepted_media_type = request.META.get('HTTP_ACCEPT', 'application/json')
            response.renderer_context = {
                'request': request,
                'response': response,
                'view': self,
            }

        return super().finalize_response(request, response, *args, **kwargs)


    def standard_response(self, **kwargs):
        """
        Utility method to return a standardized response.
        """
        return standard_response(**kwargs)
