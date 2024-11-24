from rest_framework.viewsets import ViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Deposit,PaymentMethod
from .serializers import DepositSerializer,PaymentMethodSerializer
from core.permissions import IsAdminOrReadCreateOnlyForRegularUsers
from shared.mixins import StandardResponseMixin


class DepositViewSet(StandardResponseMixin, ViewSet):
    """
    ViewSet for managing deposits.
    - Admin users have full access to all deposits.
    - Regular users can only create deposits and view their own deposits.
    """
    permission_classes = [IsAuthenticated, IsAdminOrReadCreateOnlyForRegularUsers]
    parser_classes = [MultiPartParser, FormParser]

    def list(self, request):
        """
        List deposits made by the authenticated user.
        """
        if getattr(self, 'swagger_fake_view', False): 
            return Response([], status=status.HTTP_200_OK)
        
        user = request.user
        deposits = Deposit.objects.filter(user=user).order_by('-date_time')  # Regular user: Their deposits

        serializer = DepositSerializer(deposits, many=True)
        return self.standard_response(
            success=True,
            message="Deposits retrieved successfully.", 
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def create(self, request):
        """
        Create a deposit for the authenticated user.
        """
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, status="Pending")
        
        return self.standard_response(
            success=True,
            message="Deposit created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )



class PaymentMethodViewSet(StandardResponseMixin, ViewSet):
    """
    ViewSet for managing user payment methods.
    - Users can create, view, update, and delete their payment methods.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List or create the authenticated user's payment method.
        """
        user = request.user

        # Use get_or_create to ensure a payment method exists
        payment_method, created = PaymentMethod.objects.get_or_create(
            user=user,
            defaults={
                "name": (
                    f"{user.first_name if user.first_name else ''} {user.last_name if user.last_name else ''}".strip()
                ) or user.username,
                "phone_number": getattr(user, "phone_number", ""),
                "email_address": user.email,
                "wallet": "",
                "exchange": ""
            }
        )

        # Ensure `name` is properly updated after creation
        if created:
            payment_method.name = (
                f"{user.first_name if user.first_name else ''} {user.last_name if user.last_name else ''}".strip()
            ) or user.username
            payment_method.save()

        serializer = PaymentMethodSerializer(payment_method)

        message = (
            "Payment method created successfully." if created else "Payment method retrieved successfully."
        )

        return self.standard_response(
            success=True,
            message=message,
            data=serializer.data,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
    @swagger_auto_schema(
        operation_summary="Create or Update Payment Method",
        operation_description="Create or update the authenticated user's payment method.",
        request_body=PaymentMethodSerializer,
        responses={
            201: openapi.Response(
                description="Payment method created successfully.",
                schema=PaymentMethodSerializer
            ),
            200: openapi.Response(
                description="Payment method updated successfully.",
                schema=PaymentMethodSerializer
            ),
            400: "Validation error occurred.",
        }
    )
    def create(self, request):
        """
        Create or update the authenticated user's payment method.
        """
        # Use `get_or_create` to ensure a single payment method per user
        payment_method, created = PaymentMethod.objects.get_or_create(user=request.user)
        serializer = PaymentMethodSerializer(payment_method, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        message = "Payment method created successfully." if created else "Payment method updated successfully."
        return self.standard_response(
            success=True,
            message=message,
            data=serializer.data,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
    