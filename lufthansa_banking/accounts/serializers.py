from rest_framework.serializers import ModelSerializer, ValidationError, UUIDField
from .models import Account, AccountRequest, Card, CardRequest
from users.models import CustomUser
from rest_framework.exceptions import ValidationError

class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'user', 'currency', 'balance', 'is_active', 'creation_date']
        extra_kwargs= {
            'user': {'read_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        validated_data["user"] = self.context['request'].user
        account = Account.objects.create(**validated_data)
        account.save()
        return account
    
    def validate(self, data):
        if self.context['request'].user.type == 'CUSTOMER' and not data["description"]:
            raise ValidationError("Customer can't add descriptions.")

        if self.context['request'].user.type == 'CUSTOMER':
            raise ValidationError("Customer can't create accounts.")
        return data
    
    def update(self, instance, validated_data):
        if self.context['request'].user.type == 'CUSTOMER':
            raise ValidationError("Customer can't update accounts.")
        instance.save()
        return instance

class CardSerializer(ModelSerializer):
    class Meta:
        model = Card
        fields = ['card_type', 'account', 'card_number', 'cvv']
        
    def validate(self, attrs):
        account = Account.objects.get(account=attrs.pop('account'))
        if account.exists():
            raise ValidationError("Account does not exist.")

        if account.user != self.context['request'].user:
            raise ValidationError("You can only request a card for your own account.")

class CardRequestSerializer(ModelSerializer):
    account = UUIDField()
    class Meta:
        model = CardRequest
        fields = ['id', 'card_type', 'account', 'user_salary', 'salary_currency']

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

    def validate(self, attrs):
        if self.context['request'].user.type == 'CUSTOMER' and not attrs["description"]:
            raise ValidationError("Customer can't add descriptions.")

        if Account.objects.get(id=str(attrs['account'])).user != self.context['request'].user and self.context['request'].user.type not in ["ADMIN", "BANKER"]:
            raise ValidationError("You can only request a card for your own account.")
        return attrs

class AccountRequestSerializer(ModelSerializer):
    class Meta:
        model = AccountRequest
        fields = ['id', 'account_type', 'initial_deposit', 'currency', 'description']
        extra_kwargs= {
            'user': {'read_only': True},
            'id': {'read_only': True},
        }

    def validate(self, data):
        if self.context['request'].user.type == 'CUSTOMER' and not data["description"]:
            raise ValidationError("Customer can't add descriptions.")
        return data

    def create(self, validated_data):
        validated_data["user"] = self.context['request'].user
        request = AccountRequest.objects.create(**validated_data)
        request.save()
        return request
