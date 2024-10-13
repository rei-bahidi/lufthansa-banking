from .models import Transaction
from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['from_account', 'amount', 'currency', 'transaction_type', 'to_account']

    def validate(self, data):

        if data['transaction_type'] == 'CREDT' and not data['to_account']:
            raise serializers.ValidationError({"to_account": "Cannot CREDIT without a 'to_account'."})
        
        if data['transaction_type'] == 'DEBIT' and not data['from_account']:
            raise serializers.ValidationError({"from_account": "Cannot DEBIT without a 'from_account'."})
        
        return data