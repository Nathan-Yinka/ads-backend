from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from shared.enums import GenderEnum
from shared.helpers import generate_invitation_code

class UserQuerySet(models.QuerySet):
    """
    Custom QuerySet for User model to add chainable methods.
    """
    def users(self):
        """
        Return all non-staff users.
        """
        return self.filter(is_staff=False)

class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    """

    def get_queryset(self):
        """
        Return the custom UserQuerySet for all queries.
        """
        return UserQuerySet(self.model, using=self._db)

    def users(self):
        """
        Shortcut method to directly access the `users` method of UserQuerySet.
        """
        return self.get_queryset().users()

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        username = username.strip()

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses both username and email for authentication.
    """

    username = models.CharField(max_length=30, unique=True, blank=False)
    email = models.EmailField(unique=True, blank=False)
    phone_number = models.CharField(max_length=15, unique=True, blank=False)
    first_name = models.CharField(max_length=30,blank=True,null=True)
    last_name = models.CharField(max_length=30,blank=True,null=True)
    gender = models.CharField(
        max_length=1,
        choices=GenderEnum.choices(),  
        default=GenderEnum.MALE.value 
    )
    transactional_password = models.CharField(
        max_length=4,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^\d{4}$',
                message="The transactional password must be exactly 4 digits.",
                code='invalid_length'
            )
        ]
    )
    referral_code = models.CharField(
        max_length=6,
        unique=False,
        blank=False,
        null=False,
        editable=False
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        verbose_name="Profile Picture"
    )
    last_connection = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Last Connection"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Update related_name for groups and user_permissions
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups", 
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions", 
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = generate_invitation_code()
        super().save(*args, **kwargs)

    def check_transactional_password(self,transactional_password):
        return self.transactional_password == transactional_password

    def __str__(self):
        return self.username


class Invitation(models.Model):
    """
    Model to track invitations and bonuses.
    """
    referral = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="referrals",
        verbose_name="Referrer"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="invitation",
        verbose_name="Referred User"
    )
    received_bonus = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invitation from {self.referral.username} to {self.user.username}"


class InvitationCode(models.Model):
    invitation_code = models.CharField(
        max_length=6,
        unique=False,
        blank=False,
        null=False,
        editable=False
    )
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invitation_code:
            self.invitation_code = generate_invitation_code()
        super().save(*args, **kwargs)