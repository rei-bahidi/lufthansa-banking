from django.urls import path, include
from django.contrib.auth.models import User
from .models import CustomUser, Customer, Banker
from rest_framework import routers, serializers, viewsets

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']


# Serializer for the CustomerUser model
class CustomerUserSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Customer
        fields = ['id', 'customer_specific_field']

# Serializer for the BankerUser model
class BankerUserSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Banker
        fields = ['id', 'user']
