from django.db import models
from django.core.exceptions import ValidationError
from utils import convert_currency



class Currencies(models.Model):
    currency_name = models.CharField(max_length=10, unique=True, default='Euro')
    currency_code = models.CharField(primary_key=True, unique=True, max_length=10, default='EUR')
    is_active = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        if self.currency_code == 'EUR':
            raise ValidationError("Cannot delete default currency")
        
        default_currency = Currencies.objects.get(currency_code='EUR')

        accounts = Account.objects.filter(currency=self)
        
        for account in accounts:
            new_balance = convert_currency(account.balance, self.currency_code, 'EUR')
            account.currency = default_currency
            account.balance = new_balance
            account.save()

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.is_active:
            super().save(*args, **kwargs)

        if self.currency_code == 'EUR':
            raise ValidationError("Cannot deactivate default currency")
        
        default_currency = Currencies.objects.get(currency_code='EUR')
        accounts = Account.objects.filter(currency=self)
        
        for account in accounts:
            new_balance = convert_currency(account.balance, self.currency_code, 'EUR')
            account.currency = default_currency
            account.balance = new_balance
            account.save()

        super().save(*args, **kwargs)

class Account(models.Model):
    
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey('accounts.Currencies', on_delete=models.SET_DEFAULT, default='EUR')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.currency.is_active:
            raise ValidationError("This currency is not active")

        if self.balance < 0:
            raise ValidationError("Balance cannot be negative")
        super().save(*args, **kwargs)

class Card(models.Model):
    class CardTypes(models.TextChoices):
        DEBIT = 'DEBIT', 'Debit'
        CREDIT = 'CREDIT', 'Credit'
        PREPAID = 'PREPAID', 'Prepaid'

    card_number = models.CharField(primary_key=True, max_length=16)
    card_type = models.CharField(max_length=10, choices=CardTypes.choices, default=CardTypes.DEBIT)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.account.status:
            raise ValidationError("This account is not active")
        super().save(*args, **kwargs)








