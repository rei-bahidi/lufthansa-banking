from utils import logger
from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from .permissions import IsNotOtherBanker, CustomerOnlyRead
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.views import TokenObtainPairView

class UserViewSet(ModelViewSet):
    """Viewset for User model"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # Set permission classes
    permission_classes = [IsAuthenticated ]

    def perform_create(self, serializer):
        """User POST method"""
        try:
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            print(e)
            logger('USERS').info(f"User creation problem")
            return Response({"error": "Something went wrong"}, status=500)
            
    def get_queryset(self):
        """GET, PUT, DELETE methods for User"""
        try:
            if self.request.user.type == 'ADMIN':
                custom_user = CustomUser.objects.all()
            else:
                user = self.request.user
                custom_user = CustomUser.objects.filter(id=user.id)
            if custom_user.exists():
                return custom_user
            raise CustomUser.DoesNotExist
        except Exception as e:
            print(e)
            logger('USERS').error(f"Error: {str(e)}")
            return CustomUser.objects.none()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer