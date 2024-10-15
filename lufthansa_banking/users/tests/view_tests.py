import pytest
from rest_framework.test import APIClient
from users.models import CustomUser
from django.urls import reverse
from rest_framework import status
from accounts.models import Currencies


@pytest.fixture
def user():
    """Create a test user."""
    return Currencies.objects.create(currency_name='Euro', currency_code='EUR', is_active=True)

@pytest.fixture
def api_client():
    """Fixture that provides a DRF test client."""
    return APIClient()

@pytest.fixture
def create_admin_user():
    """Fixture to create an admin user."""
    def create_admin():
        return CustomUser.objects.create_user(
            username="admin",
            password="adminpassword",
            email="admin@test.com",
            type="ADMIN"
        )
    return create_admin

@pytest.fixture
def create_banker_user():
    """Fixture to create a banker user."""
    def create_banker():
        return CustomUser.objects.create_user(
            username="banker",
            password="bankerpassword",
            email="banker@test.com",
            type="BANKER"
        )
    return create_banker

@pytest.fixture
def create_customer_user():
    """Fixture to create a customer user."""
    def create_customer():
        return CustomUser.objects.create_user(
            username="customer",
            password="customerpassword",
            email="customer@test.com",
            type="CUSTOMER"
        )
    return create_customer

@pytest.mark.django_db
def test_admin_can_create_user(api_client, create_admin_user):
    """Test if an admin can create a user."""
    admin_user = create_admin_user()
    api_client.force_authenticate(user=admin_user)

    url = reverse('user-list')
    data = {
        "username": "newuser",
        "password": "password",
        "email": "newuser@test.com",
        "type": "CUSTOMER"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.count() == 2


@pytest.mark.django_db
def test_banker_cannot_create_admin(api_client, create_banker_user):
    """Test if a banker cannot create an admin."""
    banker_user = create_banker_user()
    api_client.force_authenticate(user=banker_user)

    url = reverse('user-list')
    data = {
        "username": "adminuser",
        "password": "adminpassword",
        "email": "adminuser@test.com",
        "type": "ADMIN"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "Something went wrong"


@pytest.mark.django_db
def test_customer_cannot_create_user(api_client, create_customer_user):
    """Test if a customer cannot create a user."""
    customer_user = create_customer_user()
    api_client.force_authenticate(user=customer_user)

    url = reverse('user-list')
    data = {
        "username": "user1",
        "password": "password",
        "email": "user1@test.com",
        "type": "CUSTOMER"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "Something went wrong"


@pytest.mark.django_db
def test_get_user_queryset_for_admin(api_client, create_admin_user):
    """Test if an admin can retrieve all users."""
    admin_user = create_admin_user()
    api_client.force_authenticate(user=admin_user)

    url = reverse('user-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == CustomUser.objects.count()


@pytest.mark.django_db
def test_get_user_queryset_for_banker(api_client, create_banker_user, create_customer_user):
    """Test if a banker can retrieve only customer users."""
    banker_user = create_banker_user()
    customer_user = create_customer_user()
    api_client.force_authenticate(user=banker_user)

    url = reverse('user-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == CustomUser.objects.filter(type="CUSTOMER").count()


@pytest.mark.django_db
def test_get_user_queryset_for_customer(api_client, create_customer_user):
    """Test if a customer can retrieve only their own details."""
    customer_user = create_customer_user()
    api_client.force_authenticate(user=customer_user)

    url = reverse('user-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['username'] == customer_user.username


@pytest.mark.django_db
def test_token_obtain_pair(api_client, create_customer_user):
    """Test obtaining a token pair for a user."""
    user = create_customer_user()

    url = reverse('token_obtain_pair')
    data = {
        "username": user.username,
        "password": "customerpassword"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_token_obtain_pair_invalid_credentials(api_client, create_customer_user):
    """Test obtaining token pair with invalid credentials."""
    user = create_customer_user()

    url = reverse('token_obtain_pair')
    data = {
        "username": user.username,
        "password": "wrongpassword"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data