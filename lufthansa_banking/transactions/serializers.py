from .models import Transaction
from rest_framework.serializers import ModelSerializer, ValidationError
from accounts.models import Account
from uuid import UUID

class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['from_account', 'amount', 'currency', 'transaction_type', 'to_account']

    def validate(self, data):
        if data["amount"] <= 0:
            raise ValidationError("Amount must be greater than 0.")

        if data.get('from_account') and data["from_account"].user != self.context['request'].user and self.context['request'].user.type == 'CUSTOMER':
            raise ValidationError("You can only debit from your own account.")

        if data['transaction_type'] == 'CREDIT' and not data['to_account']:
            raise ValidationError({"to_account": "Cannot CREDIT without a 'to_account'."})
        
        if data['transaction_type'] == 'DEBIT' and not data['from_account']:
            raise ValidationError({"from_account": "Cannot DEBIT without a 'from_account'."})
        
        return data