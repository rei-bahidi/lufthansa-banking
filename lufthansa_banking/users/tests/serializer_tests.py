import pytest
from users.models import CustomUser
from users.serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from rest_framework.serializers import ValidationError


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testuser@example.com',
        'password': 'testpassword',
        'type': 'CUSTOMER'
    }

@pytest.mark.django_db
def test_valid_user_serializer(user_data):
    """Test that a valid user serializer creates a user."""
    serializer = CustomUserSerializer(data=user_data)
    assert serializer.is_valid()
    
    user = serializer.save()
    assert user.username == 'testuser'
    assert user.email == 'testuser@example.com'
    assert user.check_password('testpassword')  
    assert user.type == 'CUSTOMER'


@pytest.mark.django_db
def test_user_serializer_duplicate_email(user_data):
    """Test that creating a user with a duplicate email raises a ValidationError."""
    CustomUser.objects.create(**user_data)  
    user_data["username"] = "testerrr"
    serializer = CustomUserSerializer() 

    with pytest.raises(ValidationError) as excinfo:
        serializer.validate(user_data)
    
    assert str(excinfo.value) == '[ErrorDetail(string="Something went wrong: [ErrorDetail(string=\'A user with this email already exists.\', code=\'invalid\')]", code=\'invalid\')]'


@pytest.mark.django_db
def test_user_serializer_missing_required_fields():
    """Test that the serializer raises a ValidationError when required fields are missing."""
    incomplete_data = {
        'email': 'testuser@example.com',
        'password': 'testpassword',
    }

    serializer = CustomUserSerializer(data=incomplete_data)
        
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)
    
    assert 'username' in excinfo.value.detail



@pytest.mark.django_db
def test_token_obtain_pair_serializer(user_data):
    """Test that the CustomTokenObtainPairSerializer works correctly."""
    user = CustomUser.objects.create_user(**user_data)  # Create a user to authenticate

    serializer = CustomTokenObtainPairSerializer.get_token(user)
    assert serializer['type'] == user.type
    assert 'exp' in serializer  
    assert 'jti' in serializer  