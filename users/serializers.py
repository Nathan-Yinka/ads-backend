from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

from .models import Invitation,InvitationCode
from wallet.models import Wallet
from wallet.serializers import WalletSerializer
from administration.serializers import SettingsSerializer
from shared.helpers import get_settings
from shared.mixins import AdminPasswordMixin
from game.models import Product,Game
from django.utils.timezone import now, timedelta
from django.db.models import Q
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count
from finances.models import PaymentMethod
from finances.serializers import PaymentMethodSerializer



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

    def validate_transactional_password(self,value):
        if len(value) < 4:
            raise serializers.ValidationError("The transactional password must be exactly 4 characters long")
        if len(value) != 4:
            raise serializers.ValidationError("The transactional password must be exactly 4 characters long")
        return value


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
        # print("the code is here ",value)
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
            raise serializers.ValidationError({"username_or_email": "Your account is currently is inactive."})

        attrs['user'] = user
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer.UserWalletSerializer(read_only=True) 
    settings = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id','username','email','phone_number','first_name','last_name','gender','referral_code','profile_picture','last_connection','is_active','date_joined','wallet','settings']
        read_only_fields = ['date_joined','referral_code']
        ref_name = "UserProfileSerializer "
    
    def get_settings(self,obj):
        instance = get_settings()
        if not instance:
            raise NotFound(detail="Settings not found.")
        serializer = SettingsSerializer(instance=instance)
        return serializer.data

class UserPartialSerilzer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "last_name",
            "first_name",
            "is_active"
        ]


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


class ChangeTransactionalPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        """
        Validate the current password.
        """
        user = self.context['request'].user
        if not user.check_transactional_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    def validate_new_password(self, value):
        """
        Validate the new password (add strength checks if needed).
        """
        # Example of a custom password strength check
        if len(value) < 4:
            raise serializers.ValidationError("The new password must be at least 4 characters long.")
        if len(value) != 4:
            raise serializers.ValidationError("The transactional password must be exactly 4 characters long")
        return value

    def save(self):
        """
        Update the user's password.
        """
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.transactional_password = new_password
        user.save()


class InvitationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationCode
        fields = ['id', 'invitation_code', 'is_used', 'created_at'] 



# ----------------------------------- Admin Serializers -----------------------------------------

class DashboardSerializer(serializers.Serializer):
    """
    Serializer for admin dashboard data.
    """
    total_users = serializers.SerializerMethodField()
    active_products = serializers.SerializerMethodField()
    total_submissions = serializers.SerializerMethodField()
    total_users_login_today = serializers.SerializerMethodField()
    user_registrations_per_month = serializers.SerializerMethodField()
    total_submissions_per_month = serializers.SerializerMethodField()

    def get_total_users(self, obj):
        # Replace with actual logic to calculate total users
        return User.objects.users().count()

    def get_active_products(self, obj):
        # Replace with actual logic to calculate active users
        return Product.objects.count()

    def get_total_submissions(self, obj):
        # Calculate the start of today
        start_of_today = now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = start_of_today + timedelta(days=1)

        # Query to count games created today with `played=True` or `pending=True`
        count = Game.objects.filter(
            updated_at__gte=start_of_today,  # From start of today
            updated_at__lt=end_of_today,    # Until the end of today
        ).filter(
            Q(played=True) | Q(pending=True)  # Either played or pending
        ).count()
        return count
    
    def get_total_users_login_today(self, obj):
        """
        Count the total number of users who logged in today based on their `last_connection` field.
        """
        # Calculate the start and end of today
        start_of_today = now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = start_of_today + timedelta(days=1)

        # Filter users whose last_connection is within today's range
        return User.objects.users.filter(
            last_connection__gte=start_of_today,
            last_connection__lt=end_of_today,
        ).count()

    def get_user_registrations_per_month(self, obj):
        """
        Get the number of users registered per month for the current year,
        up to the current month.
        """
        current_year = now().year
        current_month = now().month

        # Aggregate data grouped by month
        registrations = User.objects.filter(
            date_joined__year=current_year
        ).annotate(
            month=ExtractMonth('date_joined')  # Extract month from date_joined
        ).values(
            'month'
        ).annotate(
            count=Count('id')  # Count users for each month
        ).order_by('month')

        # Initialize all months up to the current month with 0
        result = {month: 0 for month in range(1, current_month + 1)}

        # Update the result with actual counts
        for reg in registrations:
            if reg['month'] <= current_month:  # Ensure only months up to the current month are included
                result[reg['month']] = reg['count']

        return result
        
    def get_total_submissions_per_month(self, obj):
        """
        Get the total number of submissions per month for the current year.
        Includes submissions where played=True or pending=True.
        """
        current_year = now().year
        current_month = now().month

        # Query for submissions grouped by month
        submissions = Game.objects.filter(
            updated_at__year=current_year,  # Filter by current year
        ).filter(
            Q(played=True) | Q(pending=True)  # Filter for played or pending
        ).annotate(
            month=ExtractMonth('updated_at')  # Group by month
        ).values(
            'month'
        ).annotate(
            count=Count('id')  # Count games for each month
        ).order_by('month')

        # Format the result for only the months up to the current month
        result = {month: 0 for month in range(1, current_month + 1)}
        for submission in submissions:
            if submission['month'] <= current_month:  # Ensure only months up to the current month are included
                result[submission['month']] = submission['count']

        return result


class AdminAuthSerializer:

    class Login(UserLoginSerializer):
        """
        Serializer for admin login, ensuring only staff users can authenticate.
        """

        def validate(self, attrs):
            # Call the base class validate method to perform the standard validation
            attrs = super().validate(attrs)

            # Additional validation for admin users
            user = attrs.get('user')
            if not user.is_staff:
                raise serializers.ValidationError({"username_or_email": "Access restricted to admin users only."})

            return attrs
    
    class Write(serializers.ModelSerializer):
        """
        Serializer for creating or updating admin users.
        """

        class Meta:
            model = User
            fields = ['id', 'username', 'email', 'is_staff', 'is_active','phone_number','first_name','last_name','profile_picture']
            read_only_fields = ['is_staff', 'is_active']
            ref_name = "Admin User - Write"

    class List(Write):
        dashboard = DashboardSerializer(source='*')
        """
        Serializer for listing admin users.
        """
        class Meta:
            model = User
            fields = ['id', 'username', 'email', 'is_staff', 'is_active','phone_number','first_name','last_name','profile_picture','dashboard']
            ref_name = "Admin User - List"


class UserProfileListSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer.UserWalletSerializer(read_only=True) 
    total_play = serializers.SerializerMethodField(read_only=True)
    total_available_play = serializers.SerializerMethodField(read_only=True)
    total_product_submitted = serializers.SerializerMethodField(read_only=True)
    total_negative_product_submitted = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id','username','email','phone_number','first_name','last_name','gender','referral_code','profile_picture','last_connection','is_active','date_joined','wallet','total_play','total_available_play','total_product_submitted','total_negative_product_submitted']
        read_only_fields = ['date_joined','referral_code',]

    def get_total_play(self,obj):
        return Game.count_games_played_today(obj)

    def get_total_available_play(self,obj):
        try:
            wallet = obj.wallet
            return wallet.package.daily_missions
        except Wallet.DoesNotExist:
            return None

    def get_total_negative_product_submitted(self,obj):
        return Game.objects.filter(user=obj,special_product=True,played=True).count()

    def get_total_product_submitted(Self,obj):
        return Game.objects.filter(user=obj,played=True).count()

class AdminUserUpdateSerializer:

    class LoginPassword(serializers.Serializer):
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)
        password = serializers.CharField(write_only=True, required=True)

        def save(self):
            """
            Update the password of the user.
            """
            user = self.validated_data['user']  # This will give you the user instance
            new_password = self.validated_data['password']
            user.set_password(new_password)
            user.save()
            return user
        
    class WithdrawalPassword(serializers.Serializer):
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)
        password = serializers.CharField(write_only=True, required=True)

        def save(self):
            """
            Update the password of the user.
            """
            user = self.validated_data['user']  # This will give you the user instance
            new_password = self.validated_data['password']
            user.transactional_password = new_password
            user.save()
            return user
        
    class UserBalance(AdminPasswordMixin,serializers.Serializer):
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)
        balance = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
        reason = serializers.CharField(required=True)

        def save(self):
            """
            Update the balance for the given user and record the reason.
            """
            user = self.validated_data['user']
            new_balance = self.validated_data['balance']
            reason = self.validated_data['reason']
            try:
                wallet = user.wallet
            except Wallet.DoesNotExist:
                wallet = Wallet.objects.create(user=user)
            wallet.balance = new_balance
            user.save()
            wallet.save()

            return user
        
    class UserProfit(AdminPasswordMixin,serializers.Serializer):
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)
        profit = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
        reason = serializers.CharField(required=True)

        def save(self):
            """
            Update the balance for the given user and record the reason.
            """
            user = self.validated_data['user']
            new_balance = self.validated_data['profit']
            reason = self.validated_data['reason']
            try:
                wallet = user.wallet
            except Wallet.DoesNotExist:
                wallet = Wallet.objects.create(user=user)
            wallet.commission = new_balance
            user.save()
            wallet.save()
            
            return user
        
    class UserSalary(AdminPasswordMixin,serializers.Serializer):
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)
        salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
        reason = serializers.CharField(required=True)

        def save(self):
            """
            Update the salary for the given user and record the reason.
            """
            user = self.validated_data['user']
            new_balance = self.validated_data['salary']
            reason = self.validated_data['reason']
            try:
                wallet = user.wallet
            except Wallet.DoesNotExist:
                wallet = Wallet.objects.create(user=user)
            wallet.salary = new_balance
            user.save()
            wallet.save()
            
            return user

    class UserProfile(serializers.Serializer):
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)

        def save(self):
            """
            Get all the user datails
            """
            user = self.validated_data['user']

            return user
        
    class UserProfileRetrieve(UserProfileListSerializer):
        use_payment_method = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = User
            fields = "__all__"
            ref_name = "Admin User Retrieve"

        def get_use_payment_method(self,obj):
            try:
                method = obj.payment_method
            except PaymentMethod.DoesNotExist:
                method = PaymentMethod.objects.create(user=obj)

            return PaymentMethodSerializer(instance=method).data

    class ToggleRegBonus(AdminPasswordMixin,serializers.Serializer):
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)

        def save(self):
            """
            Get all the user datails
            """
            user = self.validated_data['user']
            if user.is_reg_balance_add:
                new_balance = user.wallet.balance - user.reg_balance_amount
                user.is_reg_balance_add = False
                user.wallet.balance = new_balance
                user.wallet.save()
                
            else:
                new_balance = user.wallet.balance + user.reg_balance_amount
                user.is_reg_balance_add = True
                user.wallet.balance = new_balance
                user.wallet.save()

            user.save()
            return user
        
    class ToggleUserMinBalanceForSubmission(serializers.Serializer):
        user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=True)

        def save(self):
            """
            Get all the user datails
            """
            user = self.validated_data['user']
            if user.is_min_balance_for_submission_removed:
                user.is_min_balance_for_submission_removed = False
            else:
                user.is_min_balance_for_submission_removed = True

            user.save()
            return user

