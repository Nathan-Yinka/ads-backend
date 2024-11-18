from rest_framework.viewsets import GenericViewSet,ViewSet
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Settings
from .serializers import SettingsSerializer,DepositSerializer
from shared.utils import standard_response as Response
from shared.helpers import get_settings
from shared.mixins import StandardResponseMixin
from core.permissions import IsSiteAdmin
from finances.models import Deposit



class SettingsViewSet(GenericViewSet):
    """
    ViewSet for managing the global Settings instance.
    Provides GET (retrieve) and PUT (update) operations at /settings/.
    """
    permission_classes = [IsAuthenticated, IsSiteAdmin]
    
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET request for /settings.
        """
        instance = get_settings()
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
        instance =get_settings()
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

class AdminDepositViewSet(StandardResponseMixin, ViewSet):
    """
    Admin ViewSet for listing all deposits and updating the status of a deposit instance.
    """
    permission_classes = [IsSiteAdmin]

    def get_serializer_class(self):
        """
        Map the action to the appropriate serializer class.
        """
        action_to_serializer = {
            "list": DepositSerializer.List,
            "update_status": DepositSerializer.UpdateStatus,
        }
        return action_to_serializer.get(self.action, DepositSerializer.List)

    def list(self, request):
        """
        List all deposits for admin users.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Response([], status=status.HTTP_200_OK)

        deposits = Deposit.objects.all().order_by('-date_time')
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(deposits, many=True)
        return Response(
            success=True,
            message="All deposits retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="update-status")
    def update_status(self, request, pk=None):
        """
        Update the status of a specific deposit instance.
        """
        try:
            deposit = Deposit.objects.get(pk=pk)
        except Deposit.DoesNotExist:
            return Response(
                success=False,
                message="Deposit not found.",
                data={},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(deposit, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            success=True,
            message="Deposit status updated successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )