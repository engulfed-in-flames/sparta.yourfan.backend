from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth import password_validation

from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(self, user):
        token = super().get_token(user)
        token["email"] = user.email

        return token


class CreateUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        required=True,
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "nickname",
            "password1",
            "password2",
        )

    def create(self, validated_data):
        password1 = validated_data.get("password1", None)
        password2 = validated_data.get("password2", None)

        condition1 = password1 is not None and password2 is not None
        condition2 = password1 == password2

        if condition1 and condition2:
            password_validation.validate_password(password1, CustomUser)
            user = super().create(validated_data)
            if user.nickname is None:
                user.nickname = f"user#{user.pk}"
            user.set_password(password1)
            user.save()
            return user
        else:
            raise ParseError


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "nickname",
            "avatar",
        )

    def update(self, user, validated_data):
        user.nickname = validated_data.get("nickname", user.nickname)
        user.avatar = validated_data.get("avatar", user.avatar)
        user.save()
        return user


class UpdatePasswordSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        required=True,
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = (
            "password1",
            "password2",
        )

    def update(self, instance, validated_data):
        password1 = validated_data.get("password1", None)
        password2 = validated_data.get("password2", None)

        condition1 = password1 is not None and password2 is not None
        condition2 = password1 == password2

        if condition1 and condition2:
            password_validation.validate_password(password1, CustomUser)
            user = super().update(instance, validated_data)
            user.set_password(password1)
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
            "posts",
            "reports",
            "is_active",
            "is_writer",
            "is_manager",
            "is_admin",
            "user_type",
        )
