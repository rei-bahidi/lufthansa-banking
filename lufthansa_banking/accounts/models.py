from django.db import models
from django.core.exceptions import ValidationError
from utils import convert_currency
from uuid import uuid4
import random

class Currencies(models.Model):
    """
    Model representing different currencies.
    """
    currency_name = models.CharField(max_length=10, unique=True, default='Euro')
    currency_code = models.CharField(primary_key=True, unique=True, max_length=10, default='EUR')
    is_active = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        """
        Override the delete method to prevent deletion of the default currency (EUR).
        If the currency is not EUR, convert all associated account balances to EUR before deletion.
        """
        
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
        if not self.is_active and self.currency_code == 'EUR':
            raise ValidationError("Cannot deactivate default currency")
    
        super().save(*args, **kwargs)


class StatusChoices(models.TextChoices):
        """Global status choices for the account and card statuses"""
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

class Account(models.Model):
    """Account model representing a user's account"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey('accounts.Currencies', on_delete=models.SET_DEFAULT, default='EUR')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """Save account instance with validations"""
        if not self.id:
            self.id = self.generate_unique_iban()
        
        if not self.currency.is_active:
            raise ValidationError("This currency is not active")

        if self.balance < 0:
            raise ValidationError("Balance cannot be negative")
        
        super().save(*args, **kwargs)

    def generate_unique_iban(self):
        """Generate a unique IBAN for the account which is a uuid, not sure if it is the proper format but the idea stands"""
        #TODO: Could implement the proper IBAN generation from a mock API
        while True:
            id = self.generate_iban()
            if not Account.objects.filter(id=id).exists():
                return id
    
    def generate_iban(self):
        return str(uuid4().hex[:22]).upper()
    
class AccountRequest(models.Model):
    """Model representing a user's account request"""
    requested_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    account_type = models.CharField(max_length=50, default="Standard Account")
    initial_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey('accounts.Currencies', on_delete=models.SET_DEFAULT, default='EUR')
    description = models.TextField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)

    def approve(self):
        """Approve account request and create an account"""
        if self.initial_deposit < 0:
            raise ValidationError("Initial deposit cannot be negative.")


        Account.objects.create(
            balance=self.initial_deposit,
            currency=self.currency,
            user=self.user,
            is_active=True,
        )
        self.status = 'APPROVED'
        self.save()


    def reject(self, description: str):
        """Reject account request with a banker defined description"""
        self.status = 'REJECTED'
        self.description = description
        self.save()

class Card(models.Model):
    """Model representing a user's card"""
    class CardTypes(models.TextChoices):
        DEBIT = 'DEBIT', 'Debit'
        CREDIT = 'CREDIT', 'Credit'
        PREPAID = 'PREPAID', 'Prepaid'

    card_number = models.CharField(primary_key=True, max_length=16)
    card_type = models.CharField(max_length=10, choices=CardTypes.choices, default=CardTypes.DEBIT)
    cvv = models.CharField(max_length=3)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    
class CardRequest(models.Model):
    """Model representing a user's card request"""

    card_type = models.CharField(max_length=10, choices=Card.CardTypes.choices, default=Card.CardTypes.DEBIT)
    requested_at = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    user_salary = models.DecimalField(max_digits=10, decimal_places=2)
    salary_currency = models.ForeignKey('accounts.Currencies', on_delete=models.SET_DEFAULT, default='EUR')
    description = models.TextField(max_length=500, default="Lorem Ipsum")
    status = models.CharField(max_length=10, default=StatusChoices.PENDING, choices=StatusChoices)

    def approve(self):
        """Same as the account approve card request and create a card"""
        if not self.account.is_active and not self.account.status == 'APPROVED':
            raise ValidationError("Account is not active or approved.")

        if self.salary_currency.currency_code != 'EUR':
            self.user_salary = convert_currency(self.user_salary, self.salary_currency.currency_code, 'EUR')

        if self.user_salary >= 500:  
            #TODO the generation of the card data could be replaced with an 'api'-like service
            Card.objects.create(
                card_number=str(random.randint(1000000000000000, 9999999999999999)),
                card_type=self.card_type,
                cvv = str(random.randint(100, 999)),
                account=self.account, 
            )
            self.status = 'APPROVED'
            self.save()
        else:
            self.reject("Salary didn't meet the requirements")


    def reject(self, description: str):
        """Reject card request with a banker defined description"""
        self.status = 'REJECTED'
        self.description = description
        self.save()