from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TransactionSerializer, CreditTransactionSerializer, DebitTransactionSerializer
from .models import Transaction, CreditTransaction, DebitTransaction
from utils import logger, banker_required
from django.utils.decorators import method_decorator
from itertools import chain
from django.db import transaction


class TransactionListView(APIView):
    def get(self, request):
        
        try:
            debit_transactions = DebitTransaction.objects.all()
            credit_transactions = CreditTransaction.objects.all()

            debit_serializer = DebitTransactionSerializer(debit_transactions, many=True)
            credit_serializer = CreditTransactionSerializer(credit_transactions, many=True)

            transactions = list(chain(credit_serializer.data, debit_serializer.data))

            return Response(transactions)
        
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        

    def post(self, request):
        try:
            
            debit_serializer = DebitTransactionSerializer(data=request.data)
            
            if not debit_serializer.is_valid():
                return Response(debit_serializer.errors, status=400)
            
            credit_serializer = CreditTransactionSerializer(data=request.data)

            if not credit_serializer.is_valid():
                return Response(credit_serializer.errors, status=400)
            
            return Response(debit_serializer, status=201)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

class CreditTransactionListView(APIView):
    def get(self, request):
        try:
            queryset = CreditTransaction.objects.get()  # Use the get_queryset method
            serializer = CreditTransactionSerializer(queryset, many=True)  # Serialize data
            return Response(serializer.data)
        
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        
    def post(self, request):
        try:
            serializer = CreditTransactionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

class CreditTransactionView(APIView):
    def get(self, request, transaction_id):
        try:
            transaction = CreditTransaction.objects.get(pk=transaction_id)
            serializer = CreditTransactionSerializer(transaction)
            return Response(serializer.data)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

    def delete(self, request, transaction_id):
        try:
            transaction = CreditTransaction.objects.get(pk=transaction_id)
            transaction.delete()
            return Response(status=204)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

class DebitTransactionListView(APIView):

    def get(self, request):
        try:
            queryset = DebitTransaction.objects.get()  # Use the get_queryset method
            serializer = DebitTransactionSerializer(queryset, many=True)  # Serialize data
            return Response(serializer.data)
        
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        

    def post(self, request):
        try:
            serializer = DebitTransactionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)

class DebitTransactionView(APIView):
    def get(self, request, transaction_id):
        try:
            transaction = DebitTransaction.objects.get(pk=transaction_id)
            serializer = DebitTransactionSerializer(transaction)
            return Response(serializer.data)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)


    def delete(self, request, transaction_id):
        try:
            transaction = DebitTransaction.objects.get(pk=transaction_id)
            transaction.delete()
            return Response(status=204)
        except Exception as e:
            logger('USERS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)