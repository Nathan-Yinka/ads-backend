from rest_framework import serializers
from .models import Pack

class PackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pack
        fields = [
            "id", "name", "usd_value", "daily_missions","short_description", 'description',
            "daily_withdrawals", "icon", "created_by", "is_active", 
            "created_at", "updated_at"
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

class PackProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pack
        fields = ["id","name","icon","usd_value"]
