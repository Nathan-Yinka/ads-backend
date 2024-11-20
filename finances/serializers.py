from rest_framework import serializers
from .models import Deposit

class DepositSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display the username instead of the ID

    class Meta:
        model = Deposit
        fields = [
            "id", "user", "amount", "date_time", "status", "screenshot", 
            "created_at", "updated_at"
        ]
        read_only_fields = ["user", "created_at", "updated_at"]
