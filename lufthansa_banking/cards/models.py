from django.db import models
from accounts.models import Account
from django.core.exceptions import ValidationError

class Card(models.Model):
    class CardTypes(models.TextChoices):
        DEBIT = 'DEBIT', 'Debit'
        CREDIT = 'CREDIT', 'Credit'
        PREPAID = 'PREPAID', 'Prepaid'

    card_number = models.CharField(primary_key=True, max_length=16)
    card_type = models.CharField(max_length=10, choices=CardTypes.choices, default=CardTypes.DEBIT)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.account.status:
            raise ValidationError("This account is not active")
        super().save(*args, **kwargs)


