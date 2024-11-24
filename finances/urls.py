from rest_framework.routers import DefaultRouter
from .views import DepositViewSet,PaymentMethodViewSet

router = DefaultRouter()
router.register(r'deposits', DepositViewSet, basename='deposit')
router.register(r'payments', PaymentMethodViewSet, basename='deposit')

urlpatterns = router.urls
