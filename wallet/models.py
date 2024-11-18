from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Wallet(models.Model):
    """
    Wallet model to manage user's financial details.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE, 
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Wallet Balance"
    )
    on_hold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Amount On Hold"
    )
    commission = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Commission Earned"
    )
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Salary Earned"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of {self.user.username} - Balance: {self.balance}"

    def credit(self, amount):
        """
        Add funds to the wallet balance.
        """
        if amount <= 0:
            raise ValueError("Credit amount must be greater than zero.")
        self.balance += amount
        self.save()

    def debit(self, amount):
        """
        Deduct funds from the wallet balance.
        """
        if amount <= 0:
            raise ValueError("Debit amount must be greater than zero.")
        if self.balance < amount:
            raise ValueError("Insufficient balance in the wallet.")
        self.balance -= amount
        self.save()

    def add_on_hold(self, amount):
        """
        Add funds to the 'on_hold' balance.
        """
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        self.on_hold += amount
        self.save()

    def release_on_hold(self, amount):
        """
        Release funds from 'on_hold' to 'balance'.
        """
        if amount <= 0 or self.on_hold < amount:
            raise ValueError("Invalid release amount.")
        self.on_hold -= amount
        self.balance += amount
        self.save()
