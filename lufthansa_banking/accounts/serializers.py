from rest_framework import serializers
from .models import Account, Card

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_id', 'iban', 'currency', 'balance']

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['card_id', 'card_type', 'bank_account', 'salary']