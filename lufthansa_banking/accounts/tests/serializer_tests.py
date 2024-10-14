import pytest
from rest_framework.exceptions import ValidationError
from accounts.models import Account, Card, CardRequest, AccountRequest, Currencies
from accounts.serializers import AccountSerializer, CardSerializer, CardRequestSerializer, AccountRequestSerializer
from users.models import CustomUser 
from rest_framework.request import Request

@pytest.fixture
def active_currency():
    """Fixture for creating an active currency."""
    return Currencies.objects.create(currency_name='Euro', currency_code='EUR', is_active=True)
    

@pytest.fixture
def user():
    """Create a test user."""
    return CustomUser.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def account(user, active_currency):
    """Create a test account."""
    return Account.objects.create(
        user=user,
        balance=1000.00,
        currency=active_currency,  # Assuming currency is a string, adjust if it's a foreign key
        is_active=True
    )

@pytest.fixture
def card(account):
    """Create a test card."""
    return Card.objects.create(
        card_number='1234567812345678',
        card_type='DEBIT',
        cvv='123',
        account=account
    )

@pytest.mark.django_db
def test_account_serializer(account):
    """Test that the AccountSerializer works correctly."""
    serializer = AccountSerializer(account)
    assert serializer.data['id'] == str(account.id)
    assert serializer.data['balance'] == format(account.balance, '.2f')
    assert serializer.data['currency'] == account.currency.currency_code
    assert serializer.data['is_active'] == account.is_active

@pytest.mark.django_db
def test_card_serializer(card):
    """Test that the CardSerializer works correctly."""
    serializer = CardSerializer(card)
    assert serializer.data['card_number'] == card.card_number
    assert serializer.data['card_type'] == card.card_type

@pytest.mark.django_db
def test_card_request_serializer_valid(account, user):
    """Test that the CardRequestSerializer validates correctly."""
    temp_user = user
    request_data = {
        'card_type': 'DEBIT',
        'account': account.id,
        'user_salary': 600.00,
        'salary_currency': 'EUR'
    }

    class MockRequest:
        user = temp_user

    serializer = CardRequestSerializer(data=request_data, context={'request': MockRequest()})
    assert serializer.is_valid()

@pytest.mark.django_db
def test_card_request_serializer_invalid_user(account, user):
    """Test that the CardRequestSerializer raises a validation error for incorrect account ownership."""
    other_user = CustomUser.objects.create_user(
        username='otheruser',
        email='otheruser@example.com',
        password='otherpassword'
    )

    request_data = {
        'card_type': 'DEBIT',
        'account': account.id,
        'user_salary': 600.00,
        'salary_currency': 'EUR'  # Assuming currency is a string
    }

    class MockRequest:
        user = other_user

    serializer = CardRequestSerializer(data=request_data, context={'request': MockRequest()})

    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)

    assert str(excinfo.value) == "{'non_field_errors': [ErrorDetail(string='You can only request a card for your own account.', code='invalid')]}"

@pytest.mark.django_db
def test_account_request_serializer_create(user, active_currency):
    """Test that the AccountRequestSerializer creates an account request correctly."""

    temp_user = user
    request_data = {
        'account_type': 'Standard Account',
        'initial_deposit': 500.00,
        'currency': active_currency.currency_code,
        'description': 'Need a new account'
    }

    class MockRequest:
        user = temp_user

    serializer = AccountRequestSerializer(data=request_data, context={'request': MockRequest()})
    assert serializer.is_valid()

    account_request = serializer.save()
    assert account_request.user == user
    assert account_request.account_type == request_data['account_type']
    assert account_request.initial_deposit == request_data['initial_deposit']