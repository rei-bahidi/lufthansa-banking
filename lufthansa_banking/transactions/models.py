from django.db import models
from accounts.models import Account

class Transaction(models.Model):

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    isbn = models.ForeignKey('accounts.account', on_delete=models.CASCADE)
    # currency = models.CharField(max_length=10, choices=Currencies.choices, default=Currencies.DOLLAR)

    class Meta:
        abstract = True


class DebitTransaction(Transaction):


    def __str__(self):
        return "This is a debit transformation"

    class Meta:
        db_table = 'debit_transaction'


class CreditTransaction(Transaction):


    def __str__(self):
        return "This is a credit transformation"

    class Meta:
        db_table = 'credit_transaction'