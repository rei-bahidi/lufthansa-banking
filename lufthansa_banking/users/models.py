from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    USER_TYPES = (('CUSTOMER', 'Customer'), ('BANKER', 'Banker'), ('ADMIN', 'Admin'),)
    user_type = models.CharField(max_length=200, default='CUSTOMER', blank=False, choices=USER_TYPES)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions_set", 
        blank=True
    )