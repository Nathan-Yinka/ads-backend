from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import SettingsViewSet,AdminDepositViewSet

settings_viewset = SettingsViewSet.as_view({
    'get': 'retrieve',
    'patch': 'update',
})


router = DefaultRouter()
router.register(r'deposits', AdminDepositViewSet, basename='admin-deposit')


urlpatterns = [
    path('', include(router.urls)),
    path('settings/', settings_viewset, name='settings'),
]
