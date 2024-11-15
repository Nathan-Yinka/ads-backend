from django.db import models

class Settings(models.Model):
    """
    Model to store global settings for the application.
    """
    percentage_of_sponsors = models.PositiveIntegerField(default=0, verbose_name="Percentage of Sponsors")
    bonus_when_registering = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Bonus When Registering (USD)")
    service_availability_start_time = models.TimeField(verbose_name="Service Availability Start Time")
    service_availability_end_time = models.TimeField(verbose_name="Service Availability End Time")
    token_validity_period_hours = models.PositiveIntegerField(default=0, verbose_name="Token Validity Period (Hours)")
    whatsapp_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="WhatsApp Contact")
    telegram_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telegram Contact")
    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telegram Username")
    online_chat_url = models.URLField(blank=True, null=True, verbose_name="Online Chat URL")
    erc_address = models.CharField(max_length=100, blank=True, null=True, verbose_name="ERC Address")
    trc_address = models.CharField(max_length=100, blank=True, null=True, verbose_name="TRC Address")
    minimum_balance_for_submissions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Minimum Balance for Submissions")
    timezone = models.CharField(max_length=50, default="UTC", verbose_name="Time Zone")

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

    def __str__(self):
        return "Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and Settings.objects.exists():
            raise ValueError("There can only be one instance of Settings.")
        super(Settings, self).save(*args, **kwargs)
