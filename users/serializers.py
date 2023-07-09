from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, SMSAuth


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
    phone_number = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False,
    )


class SMSAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSAuth
        fields = "__all__"


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
        user = super().create(validated_data)
        password = validated_data.get("password")

        if not user.nickname:
            user.nickname = f"user#{user.pk}"

        user.set_password(password)
        user.is_active = True
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
    subscribed_boards = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "pk",
            "email",
            "nickname",
            "avatar",
            "phone_number",
            "posts",
            "subscribed_boards",
            "reports",
            "is_active",
            "is_writer",
            "is_admin",
            "user_type",
        )

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

    def get_subscribed_boards(self, obj):
        return obj.subscribed_boards.values_list(
            "pk",
            flat=True,
        )
