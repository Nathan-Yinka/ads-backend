from rest_framework import serializers
from .models import Notification
class UserNotification:
    """
    """
    
    class NotificationSerializer(serializers.ModelSerializer):
        """
        Serializer for listing all notifications.
        """
        class Meta:
            model = Notification
            fields = ['id', 'title', 'message', 'is_read', 'created_at']

    class MarkAllNotificationsAsReadSerializer(serializers.Serializer):
        """
        Serializer for marking all notifications as read.
        """
        def save(self, user):
            """
            Mark all unread notifications for the given user as read.
            """
            Notification.mark_all_user_as_read(user)

    class MarkNotificationAsReadSerializer(serializers.Serializer):
        """
        Serializer for marking a single notification as read.
        """
        notification_id = serializers.IntegerField()

        def validate_notification_id(self, value):
            """
            Validate that the notification exists and belongs to the authenticated user.
            """
            user = self.context['request'].user
            try:
                notification = Notification.objects.get(id=value, user=user,type=Notification.USER)
            except Notification.DoesNotExist:
                raise serializers.ValidationError("Notification not found.")
            return notification

        def save(self):
            """
            Mark the validated notification as read.
            """
            notification = self.validated_data['notification_id']
            notification.mark_as_read()
            return notification