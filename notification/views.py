from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from .serializers import UserNotification
from .models import Notification
from shared.mixins import StandardResponseMixin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserNotificationViewSet(StandardResponseMixin, ViewSet):
    """
    ViewSet for managing user notifications.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List all notifications for the authenticated user.
        """
        notifications = request.user.notifications.filter(type=Notification.USER).order_by('is_read', '-created_at')
        serializer = UserNotification.NotificationSerializer(notifications, many=True)
        return self.standard_response(
            success=True,
            message="All notifications have been fetched.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_as_read(self, request):
        """
        Mark all unread notifications as read for the authenticated user.
        """
        serializer = UserNotification.MarkAllNotificationsAsReadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            notifications = request.user.notifications.filter(type=Notification.USER).order_by('is_read', '-created_at')
            serializer = UserNotification.NotificationSerializer(notifications, many=True)
            return self.standard_response(
                success=True,
                message="All notifications have been marked as read.",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        return self.standard_response(
            success=False,
            message="Failed to mark notifications as read.",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        operation_id="mark_notification_as_read",
        operation_description="Marks a specific notification as read for the authenticated user.",
        request_body=UserNotification.MarkNotificationAsReadSerializer,
        responses={
            200: UserNotification.NotificationSerializer,
            400: openapi.Response("Validation Error", UserNotification.MarkNotificationAsReadSerializer),
        }
    )

    @action(detail=False, methods=["post"], url_path="mark-read")
    def mark_as_read(self, request):
        """
        Mark a single notification as read for the authenticated user.
        """
        serializer = UserNotification.MarkNotificationAsReadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            notification = serializer.save()
            serializer = UserNotification.NotificationSerializer(notification)

            return self.standard_response(
                success=True,
                message="Notification has been marked as read.",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        return self.standard_response(
            success=False,
            message="Failed to mark the notification as read.",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
