from django.db import models
from django.core.exceptions import ValidationError
from utils import convert_currency
from uuid import uuid4
from django.db import transaction

class Transaction(models.Model):
    """Transaction model to represent a financial transaction"""

    class TransactionTypes(models.TextChoices):
        """Local transaction types for the transaction model"""
        DEBIT = 'DEBIT', 'Debit'
        CREDIT = 'CREDIT', 'Credit'
        TRANSFER = 'TRANSFER', 'Transfer'

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    transaction_type = models.CharField(max_length=8, choices=TransactionTypes.choices, default=TransactionTypes.DEBIT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    from_account = models.ForeignKey('accounts.Account', related_name='from_account', null=True, on_delete=models.SET_NULL)
    to_account = models.ForeignKey('accounts.Account', related_name='to_account', null=True, on_delete=models.SET_NULL)
    
    from_account_reference = models.CharField(max_length=200, null=True)
    to_account_reference = models.CharField(max_length=200, null=True)

    currency = models.ForeignKey('accounts.Currencies', max_length=10, null=True, on_delete=models.SET_NULL)
    currency_reference = models.CharField(max_length=10, null=True)

    def validate_accounts(self):
        """Validate the accounts based on the transaction type"""
        if self.transaction_type == 'TRANSFER' and (not self.from_account or not self.to_account):
            raise ValidationError("A transfer transaction must have both 'from_account' and 'to_account'")
        
        if self.transaction_type == 'DEBIT' and not self.from_account:
            raise ValidationError("A debit transaction requires a 'from_account'.")
        
        if self.transaction_type == 'CREDIT' and not self.to_account:
            raise ValidationError("A credit transaction requires a 'to_account'.")
        
        # Ensure the accounts are active
        if self.from_account and not self.from_account.is_active:
            raise ValidationError("The 'from_account' is not active.")
        if self.to_account and not self.to_account.is_active:
            raise ValidationError("The 'to_account' is not active.")
        
    def convert_transaction_amount(self, account_currency_code):
        """Currency convertion check for the transaction amount, if not the proper currency it is converted"""
        if self.currency.currency_code != account_currency_code:
            return convert_currency(self.amount, self.currency.currency_code, account_currency_code)
        return self.amount

    def process_balance_updates(self):
        """Process the balance updates based on the transaction type""" 
        
        # debit transaction, removes money from the account
        if self.transaction_type == 'DEBIT':
            converted_amount_from = self.convert_transaction_amount(self.from_account.currency.currency_code)
            if converted_amount_from > self.from_account.balance:
                raise ValueError("Insufficient funds in 'from_account'.")
            self.from_account.balance -= converted_amount_from
            self.from_account.save()

        # credit transaction, adds money to the account
        elif self.transaction_type == 'CREDIT':
            if self.amount <= 20:
                raise ValueError("The amount is too small.")
            if self.amount > 10000:
                raise ValueError("The amount exceeds the 10,000 limit.")
            converted_amount_to = self.convert_transaction_amount(self.to_account.currency.currency_code)
            self.to_account.balance += converted_amount_to
            self.to_account.save()

        # transfer transaction, moves money from one account to another
        elif self.transaction_type == 'TRANSFER':
            converted_amount_from = self.convert_transaction_amount(self.from_account.currency.currency_code)
            if converted_amount_from > self.from_account.balance:
                raise ValueError("Insufficient funds for transfer in 'from_account'.")            
            converted_amount_to = self.convert_transaction_amount(self.to_account.currency.currency_code)
            self.from_account.balance -= converted_amount_from
            self.to_account.balance += converted_amount_to
            self.from_account.save()
            self.to_account.save()

    def save(self, *args, **kwargs):
        """All the validations are done when the transaction is saved and the transaction is processed in an atomic fashion"""
        self.validate_accounts()
        
        with transaction.atomic():
            self.set_up_transaction()
            self.process_balance_updates()
            super().save(*args, **kwargs)

    def set_up_transaction(self):
        """Set up transaction metadata in case of missing relations"""
        if not self.from_account_reference and self.from_account:
            self.from_account_reference = self.from_account.id
        
        if not self.to_account_reference and self.to_account:
            self.to_account_reference = self.to_account.id
        
        if not self.currency_reference and self.currency:
            self.currency_reference = self.currency.currency_code

    def __str__(self):
        return f"{self.transaction_type} transaction of {self.amount} on {self.date}"