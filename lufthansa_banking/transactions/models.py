from django.db import models

from utils import convert_currency

class Transaction(models.Model):

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey('accounts.Account', null=True, on_delete=models.SET_NULL)
    account_reference = models.CharField(max_length=200, default = "isb-1234")
    currency = models.ForeignKey('accounts.Currencies', max_length=10, null=True, on_delete=models.SET_NULL)
    currency_code = models.CharField(max_length=10, default='EUR')


    def save(self, *args, **kwargs):
        if self.account:
            self.account_reference = self.account.iban
        
        if self.currency:
            self.currency_code = self.currency.currency_code
        
        if not self.account.card_set.first():
            raise ValueError("The account has no card")

        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class DebitTransaction(Transaction):
    def save(self, *args, **kwargs):
        amount = self.amount

        if self.account.currency.currency_code != self.currency.currency_code:
            amount = convert_currency(amount, self.currency.currency_code, self.account.currency.currency_code)

        if amount > self.isbn.balance:
            raise ValueError("The amount is greater than the account balance")
        
        self.account.currency.balance -= amount

        super().save(*args, **kwargs)

    def __str__(self):
        return "This is a debit transformation"

    class Meta:
        db_table = 'debit_transaction'


class CreditTransaction(Transaction):
    def save(self, *args, **kwargs):
        amount = self.amount

        if self.currency.currency_code != self.account.currency.currency_code:
            amount = convert_currency(self.amount, self.currency.currency_code, self.account.currency.currency_code)

        if amount <= 20:
            raise ValueError("The amount is too small")
        
        if amount > 10000:
            raise ValueError("The amount is greater than 10000$, you cannot make transactions bigger ")

        self.account.currency.balance += amount

        super().save(*args, **kwargs)

    def __str__(self):
        return "This is a credit transformation"

    class Meta:
        db_table = 'credit_transaction'