from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import SettingsViewSet,AdminDepositViewSet,EventViewSet

router = DefaultRouter()
router.register(r'settings', SettingsViewSet, basename='settings')


router.register(r'deposits', AdminDepositViewSet, basename='admin-deposit')
router.register(r'events', EventViewSet, basename='event')


urlpatterns = [
    path('', include(router.urls)),
]
