from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(self, user):
        token = super().get_token(user)
        token["email"] = user.email

        return token


class ConvertSignupDataSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    nickname = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False,
    )


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "password",
            "nickname",
            "phone_number",
        )

    def create(self, validated_data):
        password = validated_data.get("password", None)
        user = super().create(validated_data)
        if user.nickname is None:
            user.nickname = f"user#{user.pk}"
        user.set_password(password)
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "nickname",
            "avatar",
            "phone_number",
        )

    def update(self, user, validated_data):
        user.nickname = validated_data.get("nickname", user.nickname)
        user.avatar = validated_data.get("avatar", user.avatar)
        user.phone_number = validated_data.get("phone_number", user.phone_number)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "pk",
            "email",
            "nickname",
            "is_writer",
            "is_active",
        )


class UserDetailSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()
    reports = serializers.SerializerMethodField()

    def get_posts(self, obj):
        return obj.posts.values_list(
            "pk",
            flat=True,
        )

    def get_reports(self, obj):
        return obj.reports.values_list(
            "pk",
            flat=True,
        )

    class Meta:
        model = CustomUser
        fields = (
            "pk",
            "email",
            "nickname",
            "avatar",
            "phone_number",
            "posts",
            "reports",
            "is_active",
            "is_writer",
            "is_admin",
            "user_type",
        )
