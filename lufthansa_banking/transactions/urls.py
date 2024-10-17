from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, DebitTransactionViewSet, CreditTransactionViewSet, TransferTransactionViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'debit', DebitTransactionViewSet, basename='debit')
router.register(r'credit', CreditTransactionViewSet, basename='credit')
router.register(r'transfer', TransferTransactionViewSet, basename='transfer')

urlpatterns = [
    path('', include(router.urls)),
]