import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from transactions.models import Transaction
from users.models import CustomUser
from transactions.serializers import TransactionSerializer
from accounts.models import Account, Currencies
from rest_framework.exceptions import ValidationError

@pytest.fixture
def active_currency():
    return Currencies.objects.create(currency_name='Euro', currency_code='EUR', is_active=True)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user():
    """Create an admin user"""
    return CustomUser.objects.create_user(email='admin@test.com', username="admin", password='password', type='ADMIN')

@pytest.fixture
def banker_user():
    """Create a banker user"""
    return CustomUser.objects.create_user(email='banker@test.com', username="banker", password='password', type='BANKER')

@pytest.fixture
def regular_user():
    """Create a regular user"""
    return CustomUser.objects.create_user(email='user@test.com', username="customer", password='password', type='CUSTOMER')

@pytest.fixture
def from_acccount(regular_user, active_currency):
    """Create a sample account for testing"""
    return Account.objects.create(user=regular_user, balance=1000.00, currency=active_currency, is_active=True)

@pytest.fixture
def to_account(regular_user, active_currency):
    """Create a sample account for testing"""
    return Account.objects.create(user=regular_user, balance=500.00, currency=active_currency, is_active=True)

@pytest.fixture
def create_transaction(from_acccount, to_account, active_currency):
    """Create a sample transaction for testing"""
    return Transaction.objects.create(from_account=from_acccount, to_account=to_account, currency=active_currency, amount=100)

@pytest.mark.django_db
def test_admin_can_create_transaction(api_client, from_acccount, to_account, admin_user):
    """Test that an admin can create a transaction"""
    api_client.force_authenticate(user=admin_user)
    url = reverse('transaction-list')
    data = {
        'from_account': from_acccount.id,
        'to_account': to_account.id,
        'transaction_type': 'TRANSFER',
        'currency': 'EUR',
        'amount': 100
    }
    response = api_client.post(url, data=data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Transaction.objects.count() == 1

@pytest.mark.django_db
def test_banker_can_create_transaction(api_client, from_acccount, to_account, banker_user):
    """Test that a banker can create a transaction"""
    api_client.force_authenticate(user=banker_user)
    url = reverse('transaction-list')
    data = {
        'from_account': from_acccount.id,
        'to_account': to_account.id,
        'transaction_type': 'TRANSFER',
        'currency': 'EUR',
        'amount': 200
    }
    response = api_client.post(url, data=data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Transaction.objects.count() == 1

@pytest.mark.django_db
def test_regular_user_can_create_transaction(api_client, from_acccount, to_account, regular_user):
    """Test that a regular user can create a transaction"""
    api_client.force_authenticate(user=regular_user)
    url = reverse('transaction-list')
    data = {
        'from_account': from_acccount.id,
        'to_account': to_account.id,
        'transaction_type': 'TRANSFER',
        'currency': 'EUR',
        'amount': 150
    }
    response = api_client.post(url, data=data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Transaction.objects.count() == 1

@pytest.mark.django_db
def test_transaction_creation_validation_error(api_client, from_acccount, to_account, regular_user):
    """Test that creating a transaction with invalid data raises a validation error"""
    api_client.force_authenticate(user=regular_user)
    url = reverse('transaction-list')
    data = {
        'from_account': from_acccount.id,
        'to_account': to_account.id,
        'transaction_type': 'TRANSFER',
        'currency': 'EUR',
        'amount': -100
    }
  
    response = api_client.post(url, data=data, format='json')
    assert str(response.data) == "{'non_field_errors': [ErrorDetail(string='Amount must be greater than 0.', code='invalid')]}"

@pytest.mark.django_db
def test_get_transactions_as_admin(api_client, admin_user):
    """Test that an admin can get all transactions"""
    api_client.force_authenticate(user=admin_user)
    url = reverse('transaction-list')
    
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == Transaction.objects.count()

@pytest.mark.django_db
def test_get_transactions_as_banker(api_client, banker_user):
    """Test that a banker can get all transactions"""
    api_client.force_authenticate(user=banker_user)
    url = reverse('transaction-list')
    
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == Transaction.objects.count()

@pytest.mark.django_db
def test_get_transactions_as_regular_user(api_client, regular_user, create_transaction):
    """Test that a regular user can get their own transactions"""
    api_client.force_authenticate(user=regular_user)
    url = reverse('transaction-list')
    
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

@pytest.mark.django_db
def test_delete_transaction_as_admin(api_client, admin_user, create_transaction):
    """Test that an admin can delete a transaction"""
    api_client.force_authenticate(user=admin_user)
    url = reverse('transaction-detail', args=[create_transaction.id])
    
    response = api_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Transaction.objects.count() == 0

@pytest.mark.django_db
def test_delete_transaction_as_banker(api_client, banker_user, create_transaction):
    """Test that a banker can delete a transaction"""
    api_client.force_authenticate(user=banker_user)
    transaction = create_transaction
    url = reverse('transaction-detail', args=[transaction.id])
    
    response = api_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Transaction.objects.count() == 0
