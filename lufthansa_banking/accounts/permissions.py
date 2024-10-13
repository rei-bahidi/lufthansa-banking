from rest_framework.permissions import BasePermission

class IsCardOwner(BasePermission):
    """Check if the user is the owner of the card"""
    def has_object_permission(self, request, view, obj):
        return obj.account.user == request.user

class IsAccountOwner(BasePermission):   
    """Check if the user is the owner of the account"""
    def has_object_permission(self, request, view, obj):
        return str(obj.user) == str(request.user.id)
    
class IsBankerOrAdmin(BasePermission):
    """Check if the user is a banker or an admin"""
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Bankers').exists() or \
                request.user.groups.filter(name='Administrators').exists()