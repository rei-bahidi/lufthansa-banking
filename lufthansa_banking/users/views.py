from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomUserSerializer
from .models import CustomUser
from utils import logger
from functools import wraps
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
from rest_framework import generics
from django.shortcuts import get_object_or_404


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have access to this resource.")
    return wrapped_view


def banker_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('/api-auth/login')
        
        if not request.user.user_type == 'BANKER' and \
           not request.user.is_superuser:
            return HttpResponseForbidden("You do not have access to this resource.")
        
        return view_func(request, *args, **kwargs)
    return wrapped_view

class UserListView(generics.ListAPIView):
    @method_decorator(banker_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
   
class UserView(APIView): 
    @method_decorator(banker_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        users = CustomUser.objects.filter(is_active=True)
        return users

    def get_object(self, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        return user
    
    def get(self, request, user_id):
        try:            
            user = self.get_object(user_id)
            if user:
                serializer = CustomUserSerializer(user)  # Serialize data
                return Response(serializer.data)
            return Response({"error": "User not found"}, status=404)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        
    def post(self, request):
        try:
            serializer = CustomUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        
class BankerListView(generics.ListAPIView):
    @method_decorator(admin_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    queryset = CustomUser.objects.filter(user_type='BANKER')
    serializer_class = CustomUserSerializer

class BankerView(APIView):
    @method_decorator(admin_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self, user_id=None):
        if user_id:
            return CustomUser.objects.filter(id=user_id)
        
    def get(self, request, user_id=None):
        try:
            queryset = self.get_queryset(user_id)  # Pass the user_id parameter
            if queryset:
                serializer = CustomUserSerializer(queryset, many=True)  # Serialize data
                return Response(serializer.data)
            return Response({"error": "User not found"}, status=404)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        
    def post(self, request, user_id=None):
        try:
            serializer = CustomUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)