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
        fields = ['id', 'card_type', 'account', 'user_salary', 'salary_currency']

    def validate(self, attrs):
        if Account.objects.get(id=attrs['account'].id).user != self.context['request'].user:
            raise serializers.ValidationError("You can only request a card for your own account.")
        return attrs

class AccountRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRequest
        fields = ['id', 'account_type', 'initial_deposit', 'currency', 'description']
        extra_kwargs= {
            'user': {'read_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        validated_data["user"] = self.context['request'].user
        request = AccountRequest.objects.create(**validated_data)
        request.save()
        return request