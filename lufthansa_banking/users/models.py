from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Just a user abstraction with email, first and last name as a unique field, the last two being required as well"""
    class UserTypes(models.TextChoices):
        CUSTOMER = 'CUSTOMER'
        BANKER = 'BANKER'
        ADMIN = 'ADMIN'
    
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=UserTypes.choices, default='CUSTOMER')

