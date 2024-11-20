from rest_framework.routers import DefaultRouter
from .views import DepositViewSet

router = DefaultRouter()
router.register(r'deposits', DepositViewSet, basename='deposit')

urlpatterns = router.urls
