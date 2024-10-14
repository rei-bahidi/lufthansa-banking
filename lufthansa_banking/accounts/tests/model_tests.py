import pytest
from django.core.exceptions import ValidationError
from decimal import Decimal
from accounts.models import Currencies, Account, AccountRequest, Card, CardRequest, StatusChoices

@pytest.fixture
def active_currency():
    """Fixture for creating an active currency."""
    return Currencies.objects.create(currency_name='Euro', currency_code='EUR', is_active=True)

@pytest.fixture
def inactive_currency():
    """Fixture for creating an inactive currency."""
    return Currencies.objects.create(currency_name='USD', currency_code='USD', is_active=False)

@pytest.fixture
def user():
    """Fixture for creating a mock user."""
    from users.models import CustomUser 
    return CustomUser.objects.create(username='testuser', email='test@example.com', password='testpass')

@pytest.fixture
def account(active_currency, user):
    """Fixture for creating a mock account."""
    return Account.objects.create(balance=Decimal('1000.00'), currency=active_currency, user=user, is_active=True)

@pytest.fixture
def card(account):
    from accounts.models import Card
    return Card.objects.create(card_number='1234567812345678',
                               account=account,
                               cvv='123',
                               card_type='DEBIT')

@pytest.mark.django_db
def test_currency_creation(active_currency):
    """Test creation of a currency."""
    assert active_currency.currency_name == 'Euro'
    assert active_currency.currency_code == 'EUR'
    assert active_currency.is_active is True

@pytest.mark.django_db
def test_currency_deletion(active_currency):
    """Test deletion of a non-default currency."""

    currency = Currencies.objects.create(currency_name='USD', currency_code='USD', is_active=True)
    currency.delete()
    assert Currencies.objects.filter(currency_code='USD').count() == 0

@pytest.mark.django_db
def test_currency_delete_default_currency(active_currency):
    """Test that the default currency cannot be deleted."""
    with pytest.raises(ValidationError) as excinfo:
        active_currency.delete()
    assert excinfo.value == ValidationError("Cannot delete default currency")

@pytest.mark.django_db
def test_account_creation(account):
    """Test account creation."""
    assert account.balance == Decimal('1000.00')
    assert account.currency.currency_code == 'EUR'
    assert account.user.username == 'testuser'
    assert account.is_active is True

@pytest.mark.django_db
def test_account_negative_balance(active_currency, user):
    """Test that an account cannot have a negative balance."""
    with pytest.raises(ValidationError) as excinfo:
        Account.objects.create(balance=Decimal('-100.00'), currency=active_currency, user=user)
    assert excinfo.value == ValidationError("Balance cannot be negative")

@pytest.mark.django_db
def test_account_inactive_currency(user, inactive_currency):
    """Test that an account cannot be created with an inactive currency."""
    with pytest.raises(ValidationError) as excinfo:
        Account.objects.create(balance=Decimal('100.00'), currency=inactive_currency, user=user)
    assert excinfo.value == ValidationError("This currency is not active")

@pytest.mark.django_db
def test_account_request_creation(account, user):
    """Test account request creation."""
    request = AccountRequest.objects.create(
        user=user,
        initial_deposit=Decimal('500.00'),
        currency=account.currency,
        account_type="Standard Account",
    )
    assert request.user == user
    assert request.initial_deposit == Decimal('500.00')
    assert request.status == 'PENDING'

@pytest.mark.django_db
def test_account_request_approve(account, user):
    """Test approving an account request."""
    request = AccountRequest.objects.create(
        user=user,
        initial_deposit=Decimal('500.00'),
        currency=account.currency,
    )
    request.approve()
    assert Account.objects.filter(user=user).count() == 2
    assert request.status == 'APPROVED'

@pytest.mark.django_db
def test_account_request_reject(account, user):
    """Test rejecting an account request."""
    request = AccountRequest.objects.create(
        user=user,
        initial_deposit=Decimal('500.00'),
        currency=account.currency,
    )
    request.reject("Not needed anymore.")
    assert request.status == 'REJECTED'
    assert request.description == "Not needed anymore."

@pytest.mark.django_db
def test_card_creation(account):
    """Test card creation."""
    card = Card.objects.create(card_number='1234567812345678', account=account)
    assert card.card_number == '1234567812345678'
    assert card.account == account

@pytest.mark.django_db
def test_card_request_creation(account, active_currency):
    """Test card request creation."""
    request = CardRequest.objects.create(
        card_type='DEBIT',
        account=account,
        user_salary=Decimal('600.00'),
        salary_currency=active_currency,
    )
    assert request.card_type == 'DEBIT'
    assert request.account == account
    assert request.status == StatusChoices.PENDING

@pytest.mark.django_db
def test_card_request_approve(account, active_currency):
    """Test approving a card request."""
    request = CardRequest.objects.create(
        card_type='DEBIT',
        account=account,
        user_salary=Decimal('600.00'),
        salary_currency=active_currency,
    )
    request.approve()
    assert Card.objects.filter(account=account).count() == 1
    assert request.status == 'APPROVED'

@pytest.mark.django_db
def test_card_request_reject(account, active_currency):
    """Test rejecting a card request."""
    request = CardRequest.objects.create(
        card_type='DEBIT',
        account=account,
        user_salary=Decimal('400.00'),
        salary_currency=active_currency,
    )
    request.reject("Salary too low.")
    assert request.status == 'REJECTED'
    assert request.description == "Salary too low."
