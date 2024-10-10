from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TransactionSerializer, CreditTransactionSerializer, DebitTransactionSerializer
from .models import Transaction, CreditTransaction, DebitTransaction
from utils import logger

class CreditTransaction(APIView):
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return CreditTransaction.objects.get_queryset()

    def get(self, request):
        try:
            queryset = self.get_queryset()  # Use the get_queryset method
            serializer = CreditTransactionSerializer(queryset, many=True)  # Serialize data
            return Response(serializer.data)
        
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        

    def post(self, request):
        ...