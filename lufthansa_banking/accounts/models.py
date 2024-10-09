from django.db import models

class Currencies(models.Model):
    currency_name = models.CharField(max_length=10, default='Euro')
    currency_code = models.CharField(primary_key=True, unique=True, max_length=10, default='EUR')

class Account(models.Model):
    
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey(Currencies, default=1, on_delete=models.CASCADE)
    user = models.ForeignKey('users.Customer', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    # class Meta:
    #     db_table = 'account'
