from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet

# Create a router and register the TransactionViewSet
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')

# Include the router URLs in the main URL configuration
urlpatterns = [
    path('', include(router.urls)),
]