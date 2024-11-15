from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import NotFound
from rest_framework import status
from .models import Settings
from .serializers import SettingsSerializer
from shared.utils import standard_response as Response


class SettingsViewSet(GenericViewSet):
    """
    ViewSet for managing the global Settings instance.
    Provides GET (retrieve) and PUT (update) operations at /settings/.
    """
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET request for /settings.
        """
        instance = Settings.objects.first()
        if not instance:
            raise NotFound(detail="Settings not found.")
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            message="Settings retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        """
        Handle PUT request for /settings.
        """
        instance = Settings.objects.first()
        if not instance:
            raise NotFound(detail="Settings not found.")
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            success=True,
            message="Settings updated successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
