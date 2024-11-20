from django.db import models
from django.contrib.auth import get_user_model

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
