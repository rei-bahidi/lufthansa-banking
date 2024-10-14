from .models import CustomUser
from rest_framework import serializers
from django.contrib.auth.models import Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
        }

        read_only_fields = ['id']

    
    def validate(self, data):
        if CustomUser.objects.filter(email=data["email"]).exists():
            raise ValidationError("Email already exists.")

        if data["type"] not in CustomUser.UserTypes.values:
            raise ValidationError("Not allowed user type.")

        return data


    def create(self, validated_data):
        try:
            password = validated_data.pop('password')
            user = CustomUser.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            return user
        except serializers.ValidationError as e:
            raise ValidationError({"error": "User creation failed. Please try again."})
        


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['type'] = user.type

        return token