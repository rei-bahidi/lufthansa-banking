from rest_framework.response import Response
from rest_framework.request import Request
from .serializers import CreditTransactionSerializer, DebitTransactionSerializer, TransactionSerializer, TransferTransactionSerializer
from .models import Transaction
from utils import logger
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError

class TransactionViewSet(ModelViewSet):
    """Viewset for Transaction model"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        """GET, DELETE methods for Transaction"""
        try:
            if self.request.user.type == 'ADMIN' or self.request.user.type == 'BANKER':
                return Transaction.objects.all()
            
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
        

class DebitTransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = DebitTransactionSerializer
    """Viewset for DebitTransaction model"""

    def create(self, request: Request):
        """Transaction POST method"""
        try:
            serializer = DebitTransactionSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            logger('TRANSACTIONS').error(f"Validation error: {e}")
            return Response({"detail": str(e)}, status=404)
        except Exception as e:
            logger('TRANSACTIONS').error(f"Error: {e}")
            return Response({"detail": "Something went wrong"}, status=404)

class CreditTransactionViewSet(ModelViewSet):
    """Viewset for CreditTransaction model"""
    queryset = Transaction.objects.all()
    serializer_class = CreditTransactionSerializer

    def create(self, request: Request):
        """Transaction POST method"""
        try:
            serializer = CreditTransactionSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            logger('TRANSACTIONS').error(f"Validation error: {e}")
            return Response({"detail": str(e)}, status=404)
        except Exception as e:
            logger('TRANSACTIONS').error(f"Error: {e}")
            return Response({"detail": "Something went wrong"}, status=404)

class TransferTransactionViewSet(ModelViewSet):
    """Viewset for TransferTransaction model"""
    queryset = Transaction.objects.all()
    serializer_class = TransferTransactionSerializer

    def create(self, request: Request):
        """Transaction POST method"""
        try:
            serializer = TransferTransactionSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            logger('TRANSACTIONS').error(f"Validation error: {e}")
            return Response({"detail": str(e)}, status=404)
        except Exception as e:
            logger('TRANSACTIONS').error(f"Error: {e}")
            return Response({"detail": "Something went wrong"}, status=404)