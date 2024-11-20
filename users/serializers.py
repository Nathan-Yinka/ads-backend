from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

from .models import Invitation,InvitationCode
from wallet.models import Wallet
from wallet.serializers import WalletSerializer

User = get_user_model()


class BaseAuthSerializer(serializers.Serializer):
    def validate(self, attrs):
        # Ensure username_or_email and password are not empty
        if not attrs.get('username_or_email'):
            raise serializers.ValidationError({"username_or_email": "This field is required."})
        if not attrs.get('password'):
            raise serializers.ValidationError({"password": "This field is required."})
        return attrs

class UserSignupSerializer(serializers.ModelSerializer):
    invitation_code = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'first_name', 'last_name', 'gender', 'transactional_password','invitation_code','referral_code','profile_picture']
        extra_kwargs = {
            'password': {'write_only': True},
            'transactional_password': {'write_only': True}
        }
        read_only_fields = ['referral_code','profile_picture']

    def validate_email(self, value):
        """
        Validate and normalize the email address.
        """
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        return email

    def validate_username(self, value):
        """
        Validate the username for uniqueness.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError({"username": "A user with this username already exists."})
        return value
    
    def validate_invitation_code(self, value):
        """
        Validate the invitation code.
        """
        print("the code is here ",value)
        try:
            referrer = User.objects.get(referral_code=value) 
            return referrer
        except User.DoesNotExist:
            try:
                code = InvitationCode.objects.get(invitation_code=value)
                if code.is_used:
                    raise serializers.ValidationError("The invitation code has been used")
                else:
                    return code
            except InvitationCode.DoesNotExist:
                raise serializers.ValidationError("Invalid invitation code.")

    def create(self, validated_data):
        """
        Create a new user with the validated data.
        """
        password = validated_data.pop('password')

        referrer = validated_data.pop('invitation_code')
        
        user = User.objects.create_user(password=password, **validated_data)

        # Create the invitation entry
        if isinstance(referrer,User):
            Invitation.objects.create(referral=referrer, user=user)
        if isinstance(referrer, InvitationCode):
            referrer.is_used = True
            referrer.save()

        return user


class UserLoginSerializer(BaseAuthSerializer, serializers.ModelSerializer):
    username_or_email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username_or_email', 'password']

    def validate(self, attrs):
        # Call the validation logic from BaseAuthSerializer
        attrs = super().validate(attrs)

        # Perform authentication logic or any additional validation
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        # Add your authentication logic here (example)
        user = authenticate(username=username_or_email, password=password)
        if user is None:
            raise serializers.ValidationError({"username_or_email": "Invalid credentials."})
        if not user.is_active:
            raise serializers.ValidationError({"username_or_email": "User is inactive."})

        attrs['user'] = user
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer.UserWalletSerializer(read_only=True) 
    class Meta:
        model = User
        fields = ['username','email','phone_number','first_name','last_name','gender','referral_code','profile_picture','last_connection','is_active','date_joined','wallet']
        read_only_fields = ['date_joined','referral_code']

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        """
        Validate the current password.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        """
        Validate the new password (add strength checks if needed).
        """
        # Example of a custom password strength check
        if len(value) < 1:
            raise serializers.ValidationError("New password can not be empty")
        return value

    def save(self):
        """
        Update the user's password.
        """
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()

class InvitationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationCode
        fields = ['id', 'invitation_code', 'is_used', 'created_at'] 