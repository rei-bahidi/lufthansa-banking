from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import CustomUser 
from accounts.models import Account, Card, CardRequest, AccountRequest
from transactions.models import Transaction

def create_groups_and_permissions():

        admin_group, created = Group.objects.get_or_create(name='Administrators')
        banker_group, created = Group.objects.get_or_create(name='Bankers')
        customer_group, created = Group.objects.get_or_create(name='Customers')


        user_content_type = ContentType.objects.get_for_model(CustomUser)
        transaction_content_type = ContentType.objects.get_for_model(Transaction)
        account_request_content_type = ContentType.objects.get_for_model(AccountRequest)
        account_content_type = ContentType.objects.get_for_model(Account)
        card_request_content_type = ContentType.objects.get_for_model(CardRequest)
        card_content_type = ContentType.objects.get_for_model(Card)

        user_permissions = Permission.objects.filter(content_type=user_content_type)
        transaction_permissions = Permission.objects.filter(content_type=transaction_content_type)
        account_request_permissions = Permission.objects.filter(content_type=account_request_content_type)
        account_permissions = Permission.objects.filter(content_type=account_content_type)
        card_request_permissions = Permission.objects.filter(content_type=card_request_content_type)
        card_permissions = Permission.objects.filter(content_type=card_content_type)


        admin_group.permissions.set(user_permissions)
        admin_group.permissions.set(transaction_permissions)
        admin_group.permissions.set(account_request_permissions)
        admin_group.permissions.set(account_permissions)
        admin_group.permissions.set(card_request_permissions)
        admin_group.permissions.set(card_permissions)

        banker_group.permissions.set(user_permissions)
        banker_group.permissions.set(transaction_permissions)
        banker_group.permissions.set(account_request_permissions)
        banker_group.permissions.set(account_permissions)
        banker_group.permissions.set(card_request_permissions)
        banker_group.permissions.set(card_permissions)


        customer_group.permissions.set(user_permissions)
        customer_group.permissions.set(transaction_permissions)
        customer_group.permissions.set(account_request_permissions)
        customer_group.permissions.set(account_permissions)
        customer_group.permissions.set(card_request_permissions)
        customer_group.permissions.set(card_permissions)

        
create_groups_and_permissions()