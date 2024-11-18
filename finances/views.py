from rest_framework.viewsets import ViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Deposit
from .serializers import DepositSerializer
from core.permissions import IsAdminOrReadOnlyForRegularUsers
from shared.mixins import StandardResponseMixin


class DepositViewSet(StandardResponseMixin, ViewSet):
    """
    ViewSet for managing deposits.
    - Admin users have full access to all deposits.
    - Regular users can only create deposits and view their own deposits.
    """
    permission_classes = [IsAuthenticated, IsAdminOrReadOnlyForRegularUsers]
    parser_classes = [MultiPartParser, FormParser]

    def list(self, request):
        """
        List deposits made by the authenticated user.
        """
        if getattr(self, 'swagger_fake_view', False): 
            return Response([], status=status.HTTP_200_OK)
        
        user = request.user
        if user.is_staff:
            deposits = Deposit.objects.all().order_by('-date_time')  # Admin: All deposits
        else:
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
