from utils import logger
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from django.http import HttpResponseRedirect
from .models import CustomUser
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.views import TokenObtainPairView

class UserViewSet(ModelViewSet):
    """Viewset for User model"""
    lookup_field = 'id'
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request: Request, *args, **kwargs):
        """User POST method"""
        serializer: CustomUserSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if self.request.user.type == 'CUSTOMER':
                raise ValidationError({"error": "Customer cannot create a user"})
            
            if self.request.user.type == 'BANKER' and serializer.validated_data['type'] == 'ADMIN':
                raise ValidationError({"error": "Banker cannot create an ADMIN"}, status=400)
            
            if self.request.user.type == 'BANKER' and serializer.validated_data['type'] == 'BANKER':
                raise ValidationError({"error": "Banker cannot create a BANKER"}, status=400)
            
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            logger('USERS').info(f"User creation problem", str(e))
            return Response({"error": "User couldn't be validated"}, status=400)
        except Exception as e:
            logger('USERS').info(f"User creation problem", str(e))
            return Response({"error": "Something went wrong"}, status=400)
        
    def update(self, request, *args, **kwargs):
        """User PUT method"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)

            if self.request.user.type == 'CUSTOMER':
                raise ValidationError({"error": "Customer cannot update a user"})

            if self.request.user.type == 'BANKER':
                if serializer.validated_data.get('type') in ['ADMIN', 'BANKER']:
                    raise ValidationError({"error": "Banker cannot change user type"}, status=400)

            serializer.save() 
            return Response(serializer.data, status=200)
        except ValidationError as e:
            logger('USERS').info(f"User update problem: {str(e)}")
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            logger('USERS').info(f"User update problem: {str(e)}")
            return Response({"error": "Something went wrong"}, status=400)

    def get_queryset(self):
        """GET, DELETE methods for User"""
        try:
            if self.request.user.type == 'ADMIN':
                custom_user = CustomUser.objects.all()
            elif self.request.user.type == 'BANKER':
                custom_user = CustomUser.objects.filter(type='CUSTOMER')
            else:
                user = self.request.user
                custom_user = CustomUser.objects.filter(id=user.id)
            if custom_user.exists():
                return custom_user
            raise CustomUser.DoesNotExist
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return CustomUser.objects.none()
        except CustomUser.DoesNotExist:
            logger('USERS').error("No user found")
            return CustomUser.objects.none()
        except ValidationError as e:
            logger('USERS').error(f"Error: {str(e)}")
            return CustomUser.objects.none()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer