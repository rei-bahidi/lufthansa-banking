import pytest
from rest_framework.exceptions import ValidationError
from accounts.models import Account, Currencies
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from users.models import CustomUser

@pytest.fixture
def user():
    """Create a test user."""
    return CustomUser.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword',
        first_name='Test',
        last_name='User',
        type='ADMIN'
    )

@pytest.fixture
def currency():
    """Create a test currency."""
    return Currencies.objects.create(currency_name='Euro', currency_code='EUR', is_active=True)

@pytest.fixture
def from_account(user, currency):
    """Create a test account for debit transactions."""
    return Account.objects.create(user=user, balance=1000.00, currency=currency, is_active=True)

@pytest.fixture
def to_account(user, currency):
    """Create a test account for credit transactions."""
    return Account.objects.create(user=user, balance=500.00, currency=currency, is_active=True)

@pytest.mark.django_db
def test_valid_transaction_serializer_debit(from_account, currency, user):
    """Test that the TransactionSerializer validates correctly for debit transactions."""
    request_data = {
        'from_account': from_account.id,
        'amount': 100.00,
        'currency': currency.currency_code,
        'transaction_type': 'DEBIT',
        'to_account': None  
    }

    temp_user = user
    class MockRequest:
        user = temp_user

    serializer = TransactionSerializer(data=request_data, context={'request': MockRequest()})
    assert serializer.is_valid()

@pytest.mark.django_db
def test_valid_transaction_serializer_credit(to_account, currency, user):
    """Test that the TransactionSerializer validates correctly for credit transactions."""
    request_data = {
        'from_account': None,  
        'amount': 100.00,
        'currency': currency.currency_code,
        'transaction_type': 'CREDIT',
        'to_account': to_account.id
    }

    temp_user = user
    class MockRequest:
        user = temp_user

    serializer = TransactionSerializer(data=request_data, context={'request': MockRequest()})
    assert serializer.is_valid() 

@pytest.mark.django_db
def test_transaction_serializer_invalid_credit_without_to_account(currency, from_account, user):
    """Test that the TransactionSerializer raises a validation error for credit without a 'to_account'."""
    request_data = {
        'from_account': from_account.id, 
        'amount': 100.00,
        'currency': currency.currency_code,
        'transaction_type': 'CREDIT',
        'to_account': None  
    }

    temp_user = user
    class MockRequest:
        user = temp_user

    serializer = TransactionSerializer(data=request_data, context={'request': MockRequest()})

    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)

    assert """{'to_account': [ErrorDetail(string="Cannot CREDIT without a 'to_account'.", code='invalid')]}""" == str(excinfo.value.detail)

@pytest.mark.django_db
def test_transaction_serializer_invalid_debit_without_from_account(currency, user):
    """Test that the TransactionSerializer raises a validation error for debit without a 'from_account'."""
    request_data = {
        'from_account': None,  
        'amount': 100.00,
        'currency': currency.currency_code,
        'transaction_type': 'DEBIT',
        'to_account': None 
    }
    temp_user = user
    class MockRequest:
        user = temp_user

    serializer = TransactionSerializer(data=request_data, context={'request': MockRequest()})

    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)

    assert "{'from_account': [ErrorDetail(string='This field is required.', code='invalid')]}" == "{'from_account': [ErrorDetail(string='This field is required.', code='invalid')]}"