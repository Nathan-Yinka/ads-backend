from rest_framework import serializers
from .models import Deposit,PaymentMethod
from users.serializers import UserPartialSerilzer

class DepositSerializer(serializers.ModelSerializer):
    user = UserPartialSerilzer(read_only=True)  # Display the username instead of the ID

    class Meta:
        model = Deposit
        fields = [
            "id", "user", "amount", "date_time", "status", "screenshot", 
            "created_at", "updated_at"
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentMethod with user details mapping.
    """
    name = serializers.CharField(read_only=True) 
    phone_number = serializers.CharField(read_only=True) 
    email_address = serializers.CharField(read_only=True) 

    class Meta:
        model = PaymentMethod
        fields = "__all__"
        read_only_fields = ["name", "phone_number", "email_address",'user'] 

    def save(self, **kwargs):
        """
        Save method to map user details into the PaymentMethod instance.
        """
        user = kwargs.get("user")  # Get the user from the context or kwargs
        instance = super().save(**kwargs)

        # Map user details into the PaymentMethod fields
        if user:
            instance.name = f"{user.first_name if user.first_name else ''} {user.last_name if user.last_name else ''}".strip() or user.username,
            instance.phone_number = getattr(user, "phone_number", None)
            instance.email_address = user.email
            instance.save()

        return instance
