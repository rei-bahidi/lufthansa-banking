from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    USER_TYPES = (('CUSTOMER', 'Customer'), ('BANKER', 'Banker'), ('ADMIN', 'Admin'),)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=200, default='CUSTOMER', blank=False, choices=USER_TYPES)
    is_active = models.BooleanField(default=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salary_currency = models.ForeignKey('acounts.Currencies', max_length=10, default='EUR')
    
    REQUIRED_FIELDS = ['first_name', 'last_name']

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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['first_name', 'last_name'], name='unique_name_combination')
        ]

    # def save(self, *args, **kwargs):
    #     # Check for an existing user with the same first and last name
    #     if CustomUser.objects.filter(first_name=self.first_name, last_name=self.last_name).exists():
    #         raise ValidationError("A user with this first and last name already exists.")
        
    #     super().save(*args, **kwargs)