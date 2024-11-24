from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UserNotification
from .models import Notification
from shared.mixins import StandardResponseMixin

class UserNotificationViewSet(StandardResponseMixin,ViewSet):
    """
    ViewSet for managing user notifications.
    """
    permission_classes = [IsAuthenticated]


    def list(self, request):
        """
        List all notifications for the authenticated user.
        """
        notifications = request.user.notifications.filter(type=Notification.USER).order_by('-is_read', '-created_at')
        serializer = UserNotification.NotificationSerializer(notifications, many=True)
        return self.standard_response(
                success=True,
                message="All notification as been fetched",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

    def mark_all_as_read(self, request):
        """
        Mark all unread notifications as read for the authenticated user.
        """
        serializer = UserNotification.MarkAllNotificationsAsReadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            notifications = request.user.notifications.filter(type=Notification.USER).order_by('-is_read', '-created_at')
            serializer = UserNotification.NotificationSerializer(notifications, many=True)
            return self.standard_response(
                success=True,
                message="All notification as been marked read.",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                message="Notification marked as read.",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
