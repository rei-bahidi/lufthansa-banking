from decimal import Decimal
from uuid import UUID
import pytest
from users.models import CustomUser 
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import AccountRequest, CardRequest, Account, Currencies, Card
from rest_framework import status

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
def active_currency():
    """Fixture for creating an active currency."""
    return Currencies.objects.create(currency_name='Euro', currency_code='EUR', is_active=True)

@pytest.fixture
def account(user, active_currency):
    """Create a test account."""
    return Account.objects.create(
        user=user,
        balance=1000.00,
        currency=active_currency,  
        is_active=True
    )

@pytest.fixture
def api_client():
    """Fixture to provide an authenticated API client."""
    return APIClient()

@pytest.fixture
def create_admin_user():
    """Fixture to create an admin user."""
    return CustomUser.objects.create_user(
        username="admin",
        password="adminpassword",
        email="admin@example.com",
        type="ADMIN"
    )

@pytest.fixture
def create_banker_user():
    """Fixture to create a banker user."""
    return CustomUser.objects.create_user(
        username="banker",
        password="bankerpassword",
        email="banker@example.com",
        type="BANKER"
    )

@pytest.fixture
def create_customer_user():
    """Fixture to create a customer user."""
    return CustomUser.objects.create_user(
        username="customer",
        password="customerpassword",
        email="customer@example.com",
        type="CUSTOMER"
    )

@pytest.mark.django_db
def test_approve_account_request(api_client, create_admin_user, create_banker_user, active_currency):
    """Test that an admin can approve an account request."""
    admin_user = create_admin_user
    banker_user = create_banker_user
    api_client.force_authenticate(user=admin_user)

    account_request = AccountRequest.objects.create(user=banker_user, initial_deposit=Decimal('1000.00'))

    url = reverse('approve-account-request', kwargs={'id': account_request.id})
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    account_request.refresh_from_db()
    assert account_request.status == 'APPROVED' 


@pytest.mark.django_db
def test_reject_account_request(api_client, create_admin_user, create_banker_user, active_currency):
    """Test that an admin can reject an account request."""
    admin_user = create_admin_user
    banker_user = create_banker_user
    api_client.force_authenticate(user=admin_user)

    # Create an account request
    account_request = AccountRequest.objects.create(user=banker_user, initial_deposit=Decimal('1000.00'))

    url = reverse('reject-account-request', kwargs={'id': account_request.id})
    response = api_client.post(url, data={"description": "Invalid request"})

    assert response.status_code == status.HTTP_200_OK
    account_request.refresh_from_db()
    assert account_request.status == 'REJECTED' 


@pytest.mark.django_db
def test_card_request_creation(api_client, create_banker_user, account):
    """Test that a banker can create a card request."""
    banker_user = create_banker_user
    api_client.force_authenticate(user=banker_user)

    url = reverse('card-request-list')  
    data = {
        "account": account.id,
        "card_type": "DEBIT",
        "user_salary": Decimal('600.00'),
        "salary_currency": "EUR"
    }

    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert CardRequest.objects.filter(account=account.id).exists()


@pytest.mark.django_db
def test_approve_card_request(api_client, create_admin_user, account, active_currency):
    """Test that an admin can approve a card request."""
    admin_user = create_admin_user
    api_client.force_authenticate(user=admin_user)

    card_request = CardRequest.objects.create(account=account, user_salary=Decimal(5000.00), salary_currency=active_currency, description="Approve my card")

    url = reverse('approve-card-request', kwargs={'id': card_request.id})
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    card_request.refresh_from_db()
    assert card_request.status == 'APPROVED' 


@pytest.mark.django_db
def test_reject_card_request(api_client, create_admin_user, account, active_currency):
    """Test that an admin can reject a card request."""
    admin_user = create_admin_user
    api_client.force_authenticate(user=admin_user)

    card_request = CardRequest.objects.create(account=account, user_salary=Decimal(5000.00), salary_currency=active_currency, description="Reject this card")

    url = reverse('reject-card-request', kwargs={'id': card_request.id})
    response = api_client.post(url, data={"description": "Invalid request"})

    assert response.status_code == status.HTTP_200_OK
    card_request.refresh_from_db()
    assert card_request.status == 'REJECTED'