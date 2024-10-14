import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Transaction
from accounts.models import Account, Currencies
from uuid import uuid4
from decimal import Decimal

@pytest.fixture
def active_currency():
    return Currencies.objects.create(currency_name='Euro', currency_code='EUR', is_active=True)

@pytest.fixture
def inactive_currency():
    return Currencies.objects.create(currency_name='Dollar', currency_code='USD', is_active=False)

@pytest.fixture
def user():
    from users.models import CustomUser  # Adjust the import according to your project structure
    return CustomUser.objects.create(username='testuser', email='test@example.com', password='testpass')

@pytest.fixture
def active_account(active_currency, user):
    return Account.objects.create(balance=Decimal('1000.00'), currency=active_currency, user=user, is_active=True)

@pytest.fixture
def inactive_account(active_currency, user):
    return Account.objects.create(balance=Decimal('1000.00'), currency=active_currency, user=user, is_active=False)

@pytest.mark.django_db
def test_create_debit_transaction(active_account, active_currency):
    transaction = Transaction.objects.create(transaction_type='DEBIT', amount=Decimal('100.00'), from_account=active_account, currency=active_currency)
    assert transaction.amount == Decimal('100.00')
    assert transaction.transaction_type == 'DEBIT'

@pytest.mark.django_db
def test_create_credit_transaction(active_account, active_currency):
    transaction = Transaction.objects.create(transaction_type='CREDIT', amount=Decimal('200.00'), to_account=active_account, currency=active_currency)
    assert transaction.amount == Decimal('200.00')
    assert transaction.transaction_type == 'CREDIT'

@pytest.mark.django_db
def test_create_transfer_transaction(active_account, active_currency):
    account2 = Account.objects.create(balance=Decimal('500.00'), currency=active_account.currency, user=active_account.user, is_active=True)
    transaction = Transaction.objects.create(transaction_type='TRANSFER', amount=Decimal('150.00'), from_account=active_account, to_account=account2, currency=active_currency)
    assert transaction.amount == Decimal('150.00')
    assert transaction.transaction_type == 'TRANSFER'

@pytest.mark.django_db
def test_transfer_with_inactive_from_account(inactive_account, active_currency):
    account2 = Account.objects.create(balance=Decimal('500.00'), currency=inactive_account.currency, user=inactive_account.user, is_active=True)
    with pytest.raises(ValidationError):
        Transaction.objects.create(transaction_type='TRANSFER', amount=Decimal('150.00'), from_account=inactive_account, to_account=account2, currency=active_currency)

@pytest.mark.django_db
def test_debit_transaction_validation_without_account():
    with pytest.raises(ValidationError) as excinfo:
        Transaction.objects.create(transaction_type='DEBIT', amount=Decimal('100.00'))
    assert excinfo.value == ValidationError("A debit transaction requires a 'from_account'.")

@pytest.mark.django_db
def test_credit_transaction_validation_without_account():
    with pytest.raises(ValidationError) as excinfo:
        Transaction.objects.create(transaction_type='CREDIT', amount=Decimal('100.00'))
    assert excinfo.value == ValidationError("A credit transaction requires a 'to_account'.")

@pytest.mark.django_db
def test_transfer_transaction_validation_without_accounts():
    with pytest.raises(ValidationError) as excinfo:
        Transaction.objects.create(transaction_type='TRANSFER', amount=Decimal('100.00'))
    assert excinfo.value == ValidationError("A transfer transaction must have both 'from_account' and 'to_account'")

@pytest.mark.django_db
def test_process_balance_updates_debit(active_account, active_currency):
    transaction = Transaction.objects.create(transaction_type='DEBIT', amount=Decimal('100.00'), from_account=active_account, currency=active_currency)
    transaction.process_balance_updates()
    active_account.refresh_from_db()
    assert active_account.balance == Decimal('900.00')

@pytest.mark.django_db
def test_process_balance_updates_credit(active_account, active_currency):
    transaction = Transaction.objects.create(transaction_type='CREDIT', amount=Decimal('200.00'), to_account=active_account, currency=active_currency)
    transaction.process_balance_updates()
    active_account.refresh_from_db()
    assert active_account.balance == Decimal('1200.00')

@pytest.mark.django_db
def test_process_balance_updates_transfer(active_account, active_currency):
    account2 = Account.objects.create(balance=Decimal('500.00'), currency=active_account.currency, user=active_account.user, is_active=True)
    transaction = Transaction.objects.create(transaction_type='TRANSFER', amount=Decimal('150.00'), from_account=active_account, to_account=account2, currency=active_currency)
    transaction.process_balance_updates()
    active_account.refresh_from_db()
    account2.refresh_from_db()
    assert active_account.balance == Decimal('850.00')
    assert account2.balance == Decimal('650.00')

@pytest.mark.django_db
def test_insufficient_funds_debit(active_account, active_currency):
    with pytest.raises(ValueError) as excinfo:
        Transaction.objects.create(transaction_type='DEBIT', amount=Decimal('2000.00'), from_account=active_account, currency=active_currency)
        assert excinfo.value == ValueError("Insufficient funds in 'from_account'.")

@pytest.mark.django_db
def test_amount_too_small_credit(active_account):
    with pytest.raises(ValueError) as excinfo:
        Transaction.objects.create(transaction_type='CREDIT', amount=Decimal('10.00'), to_account=active_account)
        assert excinfo.value == ValueError("The amount is too small.")

@pytest.mark.django_db
def test_amount_exceeds_limit_credit(active_account):
    with pytest.raises(ValueError) as excinfo:
        Transaction.objects.create(transaction_type='CREDIT', amount=Decimal('15000.00'), to_account=active_account)
        assert excinfo.value == ValueError("The amount exceeds the 10,000 limit.")