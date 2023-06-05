from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ParseError, ValidationError

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(self, user):
        token = super().get_token(user)
        token["email"] = user.email

        return token


class CreateUserSerializer(ModelSerializer):
    def create(self, validated_data):
        return super().create(validated_data)


class UpdateUserSerializer(ModelSerializer):
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "pk",
            "email",
            "nickname",
            "is_active",
        )


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "pk",
            "email",
            "nickname",
            "is_active",
        )
