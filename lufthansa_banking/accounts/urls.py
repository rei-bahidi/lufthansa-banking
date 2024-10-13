from django.urls import path, include
from .views import (
                    ApproveCardRequestView, 
                    ApproveAccountRequestView, 
                    RejectAccountRequestView, 
                    RejectCardRequestView, 
                    CardRequestViewSet, 
                    AccountRequestViewSet, 
                    AccountViewSet, 
                    CardViewSet
                    )
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'card_requests', CardRequestViewSet, basename='card-request')
router.register(r'account_requests', AccountRequestViewSet, basename='account-request')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'cards', CardViewSet, basename='card')

urlpatterns = [
    path('card/approve/<int:id>', ApproveCardRequestView.as_view(), name='approve-card-request'),
    path('account/approve/<int:id>', ApproveAccountRequestView.as_view(), name='approve-account-request'),
    path('account/reject/<int:id>', RejectAccountRequestView.as_view(), name='reject-account-request'),
    path('card/reject/<int:id>', RejectCardRequestView.as_view(), name='reject-card-request'),
    path('', include(router.urls)),
]
