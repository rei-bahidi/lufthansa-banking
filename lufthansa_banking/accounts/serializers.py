from rest_framework import serializers
from .models import Account, AccountRequest, Card, CardRequest

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id','user', 'balance', 'currency', 'balance', 'is_active', 'creation_date']

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['card_type', 'account', 'card_number', 'cvv']

class CardRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardRequest
        fields = ['card_type', 'account', 'user_salary', 'salary_currency', 'status']

class AccountRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRequest
        fields = ['account_type', 'initial_deposit', 'currency', 'user', 'description', 'status']