from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth import password_validation

from yourfan import settings
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
        fields = ("email", "nickname", "password1", "password2")

    def create(self, validated_data):
        user = CustomUser.objects.create_user(email=validated_data.get("email"))
        password = validated_data.get("password1", None)
        password_confirmation = validated_data.get("password2", None)

        password_validation.validate_password(password, user)
        condition1 = password is not None and password_confirmation is not None
        condition2 = password == password_confirmation
        if condition1 and condition2:
            nickname = validated_data.get("nickname", None)
            if nickname is None:
                nickname = f"user#{user.pk}"

            user.nickname = nickname
            user.set_password(password)
            user.save()
            print("F############")
            message = render_to_string(
                "signup_msg.html",
                {
                    "user": user,
                    "domain": "localhost:8000",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "email": user.email,
                },
            )
            print("A############")
            subject = "회원가입 인증 메일입니다."
            to = [user.email]
            from_email = settings.DEFAULT_FROM_EMAIL
            EmailMessage(
                subject=subject,
                body=message,
                to=to,
                from_email=from_email,
            ).send()
            print("B############")

            return user

        else:
            return ValueError("비밀번호 확인에 실패했습니다.")


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
    password_confirmation = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = CustomUser
        fields = (
            "password",
            "password_confirmation",
        )

    def update(self, user, validated_data):
        user = super().update(user, validated_data)
        password = validated_data.get("password", None)
        password_confirmation = validated_data.get("password_confirmation", None)

        password_validation.validate_password(password, user)
        condition1 = password is not None and password_confirmation is not None
        condition2 = password == password_confirmation

        if condition1 and condition2:
            user.set_password(password)
            user.save()
            return user
        else:
            return ValueError("비밀번호 확인에 실패했습니다.")


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "nickname",
            "avatar",
        )

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get("nickname", instance.nickname)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "pk",
            "email",
            "nickname",
        )


class UserDetailSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()

    def get_posts(self, obj):
        return obj.posts.values_list(
            "pk",
            flat=True,
        )

    class Meta:
        model = CustomUser
        fields = (
            "pk",
            "email",
            "nickname",
            "posts",
            "is_active",
            "is_writer",
            "is_manager",
            "is_admin",
            "username",
            "avatar",
            "like",
            "updated_at",
        )
