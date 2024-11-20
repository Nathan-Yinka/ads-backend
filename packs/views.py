from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSiteAdmin
from rest_framework.decorators import action
from rest_framework import status
from .models import Pack
from .serializers import PackSerializer
from shared.mixins import StandardResponseMixin
from rest_framework.response import Response


class PackViewSet(StandardResponseMixin, ModelViewSet):
    """
    ViewSet for managing Packs.
    """
    queryset = Pack.objects.all()
    serializer_class = PackSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        """
        Custom permission logic for different actions.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only admins can create, update, or delete packs
            return [IsSiteAdmin()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def active_packs(self, request):
        """
        Endpoint to get all active packs.
        """
        active_packs = self.queryset.filter(is_active=True).order_by('usd_value')
        serializer = self.get_serializer(active_packs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def inactive_packs(self, request):
        """
        Endpoint to get all inactive packs.
        """
        inactive_packs = self.queryset.filter(is_active=False).order_by('usd_value')
        serializer = self.get_serializer(inactive_packs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
