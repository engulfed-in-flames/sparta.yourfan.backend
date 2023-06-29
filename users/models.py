import hashlib
import hmac
import base64
import time
import datetime
import json
import requests
from random import randint


from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from django.conf import settings
from django.utils import timezone

from common.models import CommonModel


class SMSAuth(CommonModel):
    phone_number = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^010?[0-9]\d{3,4}?\d{4}$")],
        primary_key=True,
        verbose_name="휴대폰 번호",
    )
    auth_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="인증 번호",
    )
    try_count = models.IntegerField(default=5)

    def send_sms(self):
        if self.try_count <= 0:
            raise Exception("인증 가능 횟수를 초과했습니다.")
        self.try_count -= 1

        self.auth_number = randint(100000, 999999)
        self.save()

        base_url = f"https://sens.apigw.ntruss.com"
        uri = f"/sms/v2/services/{settings.NAVER_SERVICE_ID}/messages"
        url = f"{base_url}{uri}"
        timestamp = str(int(time.time() * 1000))
        access_key = settings.NAVER_ACCESS_KEY
        secret_key = settings.NAVER_SECRET_KEY
        secret_key = bytes(secret_key, "UTF-8")
        method = "POST"
        message = method + " " + uri + "\n" + timestamp + "\n" + access_key
        message = bytes(message, "UTF-8")
        signature = base64.b64encode(
            hmac.new(
                secret_key,
                message,
                digestmod=hashlib.sha256,
            ).digest()
        )
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-ncp-apigw-timestamp": timestamp,
            "x-ncp-iam-access-key": access_key,
            "x-ncp-apigw-signature-v2": signature,
        }
        body = {
            "type": "SMS",
            "from": settings.SENDER_PHONE_NUMBER,
            "content": f"[YouRFan] 인증 번호 {self.auth_number}를 입력해주세요.",
            "messages": [{"to": self.phone_number}],
        }
        requests.post(
            url=url,
            data=json.dumps(body),
            headers=headers,
        )

    @classmethod
    def compare_auth_number(cls, phone_number, auth_number):
        time_limit = timezone.now() - datetime.timedelta(minutes=5)
        result = cls.objects.filter(
            phone_number=phone_number,
            auth_number=auth_number,
            updated_at__gte=time_limit,
        ).exists()
        return result

    def __str__(self):
        return f"{self.phone_number}"

    class Meta:
        db_table = "sms_auth"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    class UserTypeChoices(models.TextChoices):
        KAKAO = (
            "kakao",
            "카카오",
        )
        GITHUB = (
            "github",
            "깃허브",
        )
        GOOGLE = (
            "google",
            "구글",
        )
        NORMAL = (
            "normal",
            "일반",
        )

    username = models.CharField(max_length=255)
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(
        "닉네임",
        max_length=255,
        null=True,
        blank=True,
    )
    avatar = models.URLField(blank=True)
    phone_number = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^010?[0-9]\d{3}?\d{4}$")],
        null=True,
        blank=True,
        verbose_name="휴대폰 번호",
    )
    user_type = models.CharField(
        max_length=15,
        choices=UserTypeChoices.choices,
        default="NORMAL",
    )

    is_writer = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "회원들"

    def activate(self):
        self.is_active = True
        self.save()
        return self
