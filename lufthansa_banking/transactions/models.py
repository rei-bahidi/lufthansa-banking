from django.db import models
from django.core.exceptions import ValidationError
from utils import convert_currency
from uuid import uuid4
from django.db import transaction

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey('accounts.Account', null=True, on_delete=models.SET_NULL)
    account_reference = models.CharField(max_length=200, default="isb-1234")
    currency = models.ForeignKey('accounts.Currencies', max_length=10, null=True, on_delete=models.SET_NULL)
    currency_code = models.CharField(max_length=10, default='EUR')

    def validate_account(self):
        amount = self.amount

        if not self.account.is_active or self.account.status != 'APPROVED':
            raise ValidationError("The account is not active")
        
        if not self.account_reference:
            self.account_reference = self.account.iban
        
        if not self.currency_code:
            self.currency_code = self.currency.currency_code
        
        if not self.account.card_set.first():
            raise ValueError("The account has no card")
        
        if self.currency.currency_code != self.account.currency.currency_code:
            amount = convert_currency(self.amount, self.currency.currency_code, self.account.currency.currency_code)

        return amount
    class Meta:
        abstract = True

class DebitTransaction(Transaction):
    def save(self, *args, **kwargs):
        
        amount = self.validate_account()

        if amount > self.isbn.balance:
            raise ValueError("The amount is greater than the account balance")
        
        with transaction.atomic():
            self.account.balance -= amount
            self.account.balance.save()
            super().save(*args, **kwargs)

    def __str__(self):
        return "This is a debit transformation"

    class Meta:
        db_table = 'debit_transaction'


class CreditTransaction(Transaction):
    def save(self, *args, **kwargs):

        amount = self.validate_account()

        if amount <= 20:
            raise ValueError("The amount is too small")
        
        if amount > 10000:
            raise ValueError("The amount is greater than 10000$, you cannot make transactions bigger ")

        with transaction.atomic():
            self.account.balance += amount
            self.account.balance.save()
            super().save(*args, **kwargs)

    def __str__(self):
        return "This is a credit transformation"

    class Meta:
        db_table = 'credit_transaction'