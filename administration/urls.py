from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SettingsViewSet

settings_viewset = SettingsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
})

urlpatterns = [
    path('settings/', settings_viewset, name='settings'),
]
