from .models import Wallet
from rest_framework import serializers
from packs.serializers import PackProfileSerializer

class WalletSerializer:

    class UserWalletSerializer(serializers.ModelSerializer):
        package = PackProfileSerializer(read_only=True)
        """
        Serializer for Wallet model.
        """
        class Meta:
            model = Wallet
            fields = ["balance","on_hold","commission","salary",'package','credit_score'] 
