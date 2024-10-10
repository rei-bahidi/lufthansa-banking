from django.urls import path, include
from .models import CustomUser
from rest_framework import routers, serializers, viewsets

class CustomUserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'user_type', 'password', 'password_confirm']
        extra_kwargs = {
            'password': {'write_only': True},
            'internal_id': {'write_only': True} 
        }

    
    def validate(self, data):
        if CustomUser.objects.filter(first_name=data['first_name'], last_name=data['last_name']).exists():
            raise serializers.ValidationError("A user with this first and last name already exists.")
        
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user