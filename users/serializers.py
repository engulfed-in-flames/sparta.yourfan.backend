from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(self, user):
        token = super().get_token(user)
        token["email"] = user.email

        return token


class CreateUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "nickname",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data["email"], nickname=validated_data["nickname"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UpdateUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "nickname",
            # "password",
        )

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get("nickname", instance.nickname)
        instance.save()
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
