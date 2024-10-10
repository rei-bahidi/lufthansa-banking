from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomUserSerializer
from .models import CustomUser
from accounts.models import Account
from utils import logger, banker_required
from django.http import HttpResponseForbidden, Http404
from django.utils.decorators import method_decorator
from accounts.serializers import AccountSerializer, CardSerializer

class UserListView(APIView):
    @method_decorator(banker_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, format=None):
        # Bankers should only see customers, admins should see all
        if request.user.is_superuser:
            users = CustomUser.objects.all()  # Admin sees all users
        else:
            users = CustomUser.objects.filter(user_type='CUSTOMER')  # Banker sees only customers
        
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # Only admins should be able to create users
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to create users.")
        
        try:
            serializer = CustomUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)


class UserView(APIView):
    @method_decorator(banker_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request, user_id, format=None):
        try:
            user = self.get_object(user_id)

            # Bankers can only interact with customer data
            if request.user.user_type == 'BANKER' and user.user_type != 'CUSTOMER':
                return HttpResponseForbidden("Bankers can only access customer data.")
            
            serializer = CustomUserSerializer(user)  # Serialize data
            return Response(serializer.data)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

    def put(self, request, user_id, format=None):
        user = self.get_object(user_id)

        if request.user.user_type == 'BANKER' and user.user_type != 'CUSTOMER':
            return HttpResponseForbidden("Bankers can only edit customer data.")

        try:
            serializer = CustomUserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        
    def delete(self, request, user_id, format=None):        
        user = self.get_object(user_id)
        if request.user.user_type == 'BANKER' and user.user_type != 'CUSTOMER':
            return HttpResponseForbidden("Bankers can only delete customer data.")

        try:
            user.delete()
            return Response(status=204)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        

