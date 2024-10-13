from .models import CustomUser
from rest_framework import serializers
from django.contrib.auth.models import Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomUserSerializer(serializers.ModelSerializer):
    roles = serializers.CharField(write_only=True, required=False)


    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'roles']
        extra_kwargs = {
            'password': {'write_only': True},
        }

        read_only_fields = ['id']

    
    def validate(self, data):
        if CustomUser.objects.filter(first_name=data['first_name'], last_name=data['last_name']).exists():
            raise serializers.ValidationError("A user with this first and last name already exists.")
        return data


    def create(self, validated_data):
        try:
            password = validated_data.pop('password')
            group_name = validated_data.pop('roles')
            user = CustomUser.objects.create(**validated_data)
            user.set_password(password)
            group = Group.objects.get(name=group_name)
            if not group:
                raise serializers.ValidationError({"roles": "One or more groups are invalid."})
            user.groups.add(group)
            user.save()
            return user
        except Group.DoesNotExist:
            raise serializers.ValidationError({"roles": "The specified group(s) do not exist."})
        except Exception as e:
            raise serializers.ValidationError(f"Something went wrong: {str(e)}")


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['type'] = user.type

        return token