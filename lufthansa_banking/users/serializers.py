from .models import CustomUser
from rest_framework.serializers import ModelSerializer, ValidationError 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError



class CustomUserSerializer(ModelSerializer):


    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate(self, data):
        try:
            if CustomUser.objects.filter(email=data['email']).exists():
                raise ValidationError("A user with this email already exists.")
            
            if data["type"] not in CustomUser.UserTypes.values:
                raise ValidationError("Not allowed user type.")
            
            if CustomUser.objects.filter(username=data['username']).exists():
                raise ValidationError("A user with this username already exists.")

            return data
        except ValidationError as e:
            raise ValidationError(f"Something went wrong: {str(e)}")

    def create(self, validated_data):
        try:
            password = validated_data.pop('password')
            user = CustomUser.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            return user
        except ValidationError as e:
            raise ValidationError(f"Something went wrong: {str(e)}")


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['type'] = user.type

        return token