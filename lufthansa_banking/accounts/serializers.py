from rest_framework import serializers
from .models import Account, AccountRequest, Card, CardRequest
from users.models import CustomUser
from rest_framework.exceptions import ValidationError

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id','user', 'balance', 'currency', 'balance', 'is_active', 'creation_date']

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['card_type', 'account', 'card_number', 'cvv']

class CardRequestSerializer(serializers.ModelSerializer):
    account = serializers.UUIDField()
    class Meta:
        model = CardRequest
        fields = ['card_type', 'account', 'user_salary', 'salary_currency']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def validate(self, data):
        account = Account.objects.get(id=data['account'])
        if account.user != self.context['request'].user:
            raise ValidationError("You are not allowed to request a card for this account.")
        return data

    def create(self, data):
        try:
            account = Account.objects.get(id=data.pop('account')) 
            data["account"] = account
            card = CardRequest.objects.create(**data)  
            card.save()
            return card
        except Account.DoesNotExist:
            raise Exception("Account with the given UUID does not exist.")
        except ValidationError as e:
            raise ValidationError({"error": "Card request failed. Please try again."})
        
   
class AccountRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRequest
        fields = ['id', 'account_type', 'initial_deposit', 'currency', 'user']
        extra_kwargs = {
            'user': {'read_only': True},
            'id': {'read_only': True}
        }

    def create(self, data):
        try:
            data["user"] = self.context['request'].user
            account = AccountRequest.objects.create(**data)
            account.save()
            return account
        except ValidationError as e:
            raise ValidationError({"error": "Account request failed. Please try again."})