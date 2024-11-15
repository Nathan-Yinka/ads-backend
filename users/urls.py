from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserAuthViewSet

# Create a router and register the UserAuthViewSet
router = DefaultRouter()
router.register(r'', UserAuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)), 
]
