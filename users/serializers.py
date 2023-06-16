from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage

from yourfan import settings
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
        )

    def create(self, validated_data):
        user = CustomUser.objects.create_user(email=validated_data.get("email"))

        password1 = validated_data.get("password1", None)
        password2 = validated_data.get("password2", None)

        condition1 = password1 is not None and password2 is not None
        condition2 = password1 == password2

        if condition1 and condition2:
            pass
        else:
            return ValueError("비밀번호 확인에 실패했습니다.")

        nickname = validated_data.get("nickname", None)

        if nickname is None:
            nickname = f"user#{user.pk}"

        user.nickname = nickname
        user.set_password(password1)
        user.save()

        message = render_to_string(
            "signup_msg.html",
            {
                "user": user,
                "domain": "localhost:8000",
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "email": user.email,
            },
        )

        subject = "회원가입 인증 메일입니다."
        to = [user.email]
        from_email = settings.DEFAULT_FROM_EMAIL
        EmailMessage(
            subject=subject,
            body=message,
            to=to,
            from_email=from_email,
        ).send()

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
