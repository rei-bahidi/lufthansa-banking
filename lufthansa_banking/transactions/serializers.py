from .models import Transaction, DebitTransaction, CreditTransaction, TransferTransaction
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

        if data['from_account'] and data["from_account"].user != self.context['request'].user and self.context['request'].user.type == 'CUSTOMER':
            raise ValidationError("You can only debit from your own account.")

        if data['transaction_type'] == 'CREDIT' and not data['to_account']:
            raise ValidationError({"to_account": "Cannot CREDIT without a 'to_account'."})
        
        if data['transaction_type'] == 'DEBIT' and not data['from_account']:
            raise ValidationError({"from_account": "Cannot DEBIT without a 'from_account'."})
        
        return data

class DebitTransactionSerializer(ModelSerializer):
    class Meta:
        model = DebitTransaction
        fields = ['from_account', 'amount', 'currency']

    def validate(self, data):

        if data["amount"] <= 0:
            raise ValidationError("Amount must be greater than 0.")

        if data['from_account'] and data["from_account"].user != self.context['request'].user and self.context['request'].user.type == 'CUSTOMER':
            raise ValidationError("You can only debit from your own account.")
        
        if not data['from_account']:
            raise ValidationError({"from_account": "Cannot DEBIT without a 'from_account'."})

        return data
    
    def create(self, validated_data):
        return super().create(validated_data)
    
class CreditTransactionSerializer(ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ['to_account', 'amount', 'currency']

    def validate(self, data):
        if data["amount"] <= 0:
            raise ValidationError("Amount must be greater than 0.")

        if data['to_account'] and data["to_account"].user != self.context['request'].user and self.context['request'].user.type == 'CUSTOMER':
            raise ValidationError("You can only credit to your own account.")
        
        if not data['to_account']:
            raise ValidationError({"to_account": "Cannot CREDIT without a 'to_account'."})

        return data
    
    def create(self, validated_data):
        return super().create(validated_data)

class TransferTransactionSerializer(ModelSerializer):
    class Meta:
        model = TransferTransaction
        fields = ['from_account', 'to_account', 'amount', 'currency']

    def validate(self, data):
        if data["amount"] <= 0:
            raise ValidationError("Amount must be greater than 0.")

        if data['from_account'] and data["from_account"].user != self.context['request'].user and self.context['request'].user.type == 'CUSTOMER':
            raise ValidationError("You can only transfer from your own account.")

        if data['to_account'] and data["to_account"].user != self.context['request'].user and self.context['request'].user.type == 'CUSTOMER':
            raise ValidationError("You can only transfer to your own account.")
        
        if not data['to_account']:
            raise ValidationError({"to_account": "Cannot CREDIT without a 'to_account'."})

        if not data['from_account']:
            raise ValidationError({"from_account": "Cannot DEBIT without a 'from_account'."})
        
        return data
    
    def create(self, validated_data):
        return super().create(validated_data)