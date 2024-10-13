from rest_framework.permissions import BasePermission

class IsTransactionOwner(BasePermission):
    """Check if the user is the owner of the transaction"""
    def has_object_permission(self, request, view, obj):
        if obj.from_account:
            return obj.from_account.user == request.user
        return obj.to_account.user == request.user