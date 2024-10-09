from django.db import models

class User(models.Model):

    class Meta:
        abstract = True

class Client(User):
    active = models.BooleanField(default=True)
    
class Banker(User):
    isbn = models.ManyToManyField('accounts.Account')
    active = models.BooleanField(default=True)