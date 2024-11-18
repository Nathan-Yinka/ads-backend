from django.contrib import admin
from .models import Deposit

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "status", "date_time", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "amount")
