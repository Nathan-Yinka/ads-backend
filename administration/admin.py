from django.contrib import admin
from .models import Settings

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for managing global settings.
    """
    list_display = [
        "percentage_of_sponsors",
        "bonus_when_registering",
        "service_availability_start_time",
        "service_availability_end_time",
        "token_validity_period_hours",
        "timezone",
    ]
    fieldsets = (
        ("General", {
            "fields": (
                "percentage_of_sponsors",
                "bonus_when_registering",
                "minimum_balance_for_submissions",
                "token_validity_period_hours",
            ),
        }),
        ("Service Availability", {
            "fields": (
                "service_availability_start_time",
                "service_availability_end_time",
                "timezone",
            ),
        }),
        ("Contacts", {
            "fields": (
                "whatsapp_contact",
                "telegram_contact",
                "telegram_username",
                "online_chat_url",
            ),
        }),
        ("Blockchain Addresses", {
            "fields": (
                "erc_address",
                "trc_address",
            ),
        }),
    )

    def has_add_permission(self, request):
        # Limit to a single instance
        return not Settings.objects.exists()
