from .models import Wallet
from rest_framework import serializers

class WalletSerializer:

    class UserWalletSerializer(serializers.ModelSerializer):
        """
        Serializer for Wallet model.
        """
        class Meta:
            model = Wallet
            fields = ["balance","on_hold","commission","salary"] 
