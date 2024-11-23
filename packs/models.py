from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Pack(models.Model):
    """
    Model to represent different membership packs.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name="Pack Name")
    usd_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="The value for the USD Valuen for th pack")
    daily_missions = models.PositiveIntegerField(verbose_name="Number of Daily Missions you can do")
    daily_withdrawals = models.PositiveIntegerField(verbose_name="NUmber of Daily Withdrawals")
    icon = models.ImageField(upload_to="pack_icons/", blank=False, null=False, verbose_name="Pack Icon")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_packs", verbose_name="Created By"
    )
    profit_percentage = models.DecimalField(
        max_digits=5,  # Adjusted for scores between 0.00 and 100.00
        decimal_places=2,
        default=0.00,
        verbose_name="Profit Per Mission",
        validators=[
            MinValueValidator(0.00),
            MaxValueValidator(100.00)
        ]
    )
    short_description = models.TextField(verbose_name="the short description for the pack")
    description = models.TextField(verbose_name="the long description for the pack")

    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.name} - {self.usd_value} USD"
    
    class Meta:
        ordering = ['usd_value']
