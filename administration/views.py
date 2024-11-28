from rest_framework.viewsets import GenericViewSet,ViewSet,ModelViewSet
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Settings,Event
from .serializers import SettingsSerializer,DepositSerializer,SettingsVideoSerializer,EventSerializer
from shared.utils import standard_response as Response
from shared.helpers import get_settings
from shared.mixins import StandardResponseMixin
from core.permissions import IsSiteAdmin,IsAdminOrReadOnly
from finances.models import Deposit
from cloudinary.uploader import upload
from rest_framework.exceptions import ValidationError



class SettingsViewSet(GenericViewSet):
    """
    ViewSet for managing the global Settings instance.
    Provides GET (retrieve), PUT (update), and POST (update video) operations.
    """
    permission_classes = [IsAuthenticated, IsSiteAdmin]
    queryset = Settings.objects.all()

    def get_serializer_class(self):
        """
        Dynamically return the appropriate serializer class based on the action.
        """
        if self.action == "retrieve":
            return SettingsSerializer
        elif self.action == "update_video":
            return SettingsVideoSerializer
        return SettingsSerializer
    
    @swagger_auto_schema(
    operation_summary="Retrieve Settings",
    operation_description="Retrieve the global settings instance.",
    responses={
        200: openapi.Response("Settings retrieved successfully", SettingsSerializer),
        404: "Settings not found",
    },
)
    def list(self, request, *args, **kwargs):
        """
        Handle GET request for settings.
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

    @action(detail=False, methods=["patch"], url_path="update-settings")
    def update_settings(self, request):
        """
        Handle PATCH request to partially update settings.
        """
        instance = get_settings()
        if not instance:
            raise NotFound(detail="Settings not found.")
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # Partial update enabled
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            success=True,
            message="Settings updated successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


    @swagger_auto_schema(
    operation_summary="Update Video",
    operation_description="Upload and update the video field in the settings.",
    manual_parameters=[
        openapi.Parameter(
            name="video",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            description="The video file to upload",
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Video updated successfully.",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Video updated successfully.",
                    "data": {
                        "video": "/media/videos/example.mp4"
                    }
                }
            },
        ),
        400: "No video file provided.",
        404: "Settings not found.",
    },)
    @action(detail=False, methods=["post"], url_path="update-video", parser_classes=[MultiPartParser, FormParser])
    def update_video(self, request):
        """
        Update the video field in the settings.
        """
        instance = Settings.objects.first()
        if not instance:
            raise NotFound(detail="Settings not found.")

        serializer = SettingsVideoSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            success=True,
            message="Video updated successfully.",
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


class EventViewSet(StandardResponseMixin,ModelViewSet):
    """
    ViewSet for managing events.
    Only admin users are allowed to access this viewset.
    """

    parser_classes = [FormParser, MultiPartParser]
    
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsSiteAdmin]