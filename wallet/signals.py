from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Wallet
from administration.models import Settings
from django.contrib.auth import get_user_model
from shared.helpers import get_settings

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Signal to create a wallet for every new user with a signup bonus.
    """
    if created:
        signup_bonus = 0.00
        try:
            settings = get_settings()
            if settings:
                signup_bonus = settings.bonus_when_registering
        except Settings.DoesNotExist:
            pass

        try:
            # Create the wallet with the signup bonus
            Wallet.objects.create(user=instance, balance=signup_bonus)
        except:
            print("An error occured trying to create user wallet")
            pass
