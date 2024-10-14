from django.core.exceptions import ValidationError
from django.db import IntegrityError
from users.models import CustomUser
import pytest

@pytest.mark.django_db
def test_create_user():
    """Test creating a user with valid details."""
    user = CustomUser.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword',
        first_name='Test',
        last_name='User'
    )
    assert user.username == 'testuser'
    assert user.email == 'testuser@example.com'
    assert user.first_name == 'Test'
    assert user.last_name == 'User'
    assert user.type == CustomUser.UserTypes.CUSTOMER

@pytest.mark.django_db
def test_create_user_with_duplicate_email():
    """Test that creating two users with the same email raises an IntegrityError."""
    CustomUser.objects.create_user(
        username='testuser1',
        email='testuser@example.com',
        password='testpassword1',
        first_name='Test1',
        last_name='User1'
    )
    
    with pytest.raises(IntegrityError):
        CustomUser.objects.create_user(
            username='testuser2',
            email='testuser@example.com',
            password='testpassword2',
            first_name='Test2',
            last_name='User2'
        )

@pytest.mark.django_db
def test_create_user_with_invalid_type():
    """Test that creating a user with an invalid type raises a ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            type='JANITOR'
        )
        user.full_clean()
    assert "'JANITOR' is not a valid choice." in str(excinfo.value)