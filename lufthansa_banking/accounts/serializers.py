from rest_framework import serializers
from .models import BankAccount, Card

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['account_id', 'iban', 'currency', 'balance', 'approved']

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['card_id', 'card_type', 'bank_account', 'salary', 'approved', 'rejection_reason']