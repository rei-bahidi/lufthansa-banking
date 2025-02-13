from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns 
from .views import UserViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)),
]
