from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractUser

from rest_framework.permissions import BasePermission

class IsNotOtherBanker(BasePermission):
    """Check if the user that is being affected is not a banker"""
    def has_object_permission(self, request, view, obj: AbstractUser):
        if request.user.groups.filter(name='Bankers').exists():
            return not obj.groups.filter(name='Bankers').exists()
        return True
    
class CustomerOnlyRead(BasePermission):
    """Check if the user is a customer and is trying to do anything besides get his own data"""
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Customers').exists() and request.method != 'GET':
            return False
        return True
    
