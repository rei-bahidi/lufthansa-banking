from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerUserSerializer
from utils import logger
from functools import wraps
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have access to this resource.")
    return wrapped_view


def banker_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You do not have access to this resource.")
        if not request.user.user_type == 'Banker':
            return HttpResponseForbidden("You do not have access to this resource.")
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


class Users(APIView):
    @method_decorator(banker_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Customer.objects.get_queryset()

    def get(self, request):
        try:
            queryset = self.get_queryset()  # Use the get_queryset method
            serializer = CustomerUserSerializer(queryset, many=True)  # Serialize data
            return Response(serializer.data)
        
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        

    def post(self, request):
        ...