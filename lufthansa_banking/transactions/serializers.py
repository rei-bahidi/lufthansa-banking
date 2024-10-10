from .models import Transaction, DebitTransaction, CreditTransaction
from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'bank_account', 'amount', 'currency', 'transaction_type', 'related_account_iban']

class DebitTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitTransaction
        fields = ['transaction_id', 'bank_account', 'amount', 'currency', 'transaction_type', 'related_account_iban']


class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ['transaction_id', 'bank_account', 'amount', 'currency', 'transaction_type', 'related_account_iban']