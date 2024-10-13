from rest_framework.response import Response

from .serializers import TransactionSerializer
from .models import Transaction
from utils import logger
from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .permissions import IsTransactionOwner
from rest_framework.exceptions import ValidationError

class TransactionViewSet(ModelViewSet):
    """Viewset for Transaction model"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: TransactionSerializer):
        """Transaction POST method"""
        try:
            serializer.save()
        except ValidationError as e:
            logger('TRANSACTIONS').error(f"Validation error: {e}")
            return Response({"detail": str(e)}, status=404)

    def get_queryset(self):
        """GET, PUT, DELETE methods for Transaction"""
        try:
            user = self.request.user
            debit_transactions = Transaction.objects.filter(from_account__user=user)
            if not debit_transactions.exists():
                raise Transaction.DoesNotExist
            
            credit_transactions = Transaction.objects.filter(to_account__user=user)
            if not credit_transactions.exists():
                raise Transaction.DoesNotExist

            return debit_transactions | credit_transactions
        except Exception as e:
            logger('TRANSACTIONS').error(f"Error: {str(e)}")
            return Transaction.objects.none()