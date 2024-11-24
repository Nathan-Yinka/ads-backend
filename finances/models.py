from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Deposit(models.Model):
    """
    Model to represent deposits made by users.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='deposits', verbose_name="User"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Amount"
    )
    date_time = models.DateTimeField(auto_now_add=True, verbose_name="Date and Time")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Status"
    )
    screenshot = models.ImageField(
        upload_to='deposit_screenshots/', null=False, blank=False, verbose_name="Screenshot"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"Deposit by {self.user.username} - {self.amount} USD - {self.status}"



class PaymentMethod(models.Model):
    """
    Model to represent a user's payment method for withdrawals.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="payment_method",
        verbose_name="User"
    )
    name = models.CharField(
        max_length=50, verbose_name="Payment Method Name"
    )
    phone_number = models.CharField(
        max_length=20, verbose_name="Phone Number", blank=True, null=True
    )
    email_address = models.EmailField(
        max_length=254, verbose_name="Email Address", blank=True, null=True
    )
    wallet = models.CharField(
        max_length=200, verbose_name="Wallet Address", blank=True, null=True
    )
    exchange = models.CharField(
        max_length=100, verbose_name="Exchange Platform", blank=True, null=True
    )
    is_active = models.BooleanField(
        default=True, verbose_name="Is Active"
    )

    def __str__(self):
        return f"{self.name} ({self.user.username})"
    

class Withdrawal(models.Model):
    """
    Model to represent withdrawals made by users.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processed', 'Processed'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='withdrawals', verbose_name="User"
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Payment Method"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Amount"
    )
    transaction_reference = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Transaction Reference",
        editable=False  # Make this field non-editable
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"Withdrawal by {self.user.username} - {self.amount} USD - {self.status}"

    def save(self, *args, **kwargs):
        """
        Auto-generate a unique transaction reference if not set.
        """
        if not self.transaction_reference:
            self.transaction_reference = str(uuid.uuid4()).replace('-', '').upper()[:12] 
        super(Withdrawal, self).save(*args, **kwargs)