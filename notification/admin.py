from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Notification model.
    """
    list_display = ('id', 'user', 'title', 'is_read', 'type', 'created_at')
    list_filter = ('is_read', 'type', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'message', 'type', 'is_read', 'created_at')
        }),
    )
