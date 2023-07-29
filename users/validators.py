import re

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from users.models import CustomUser, SMSAuth


class PasswordFormatValidator:
    def __init__(self):
        self.regex_pattern = (
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$"
        )

    def validate(self, password, user=None):
        if not re.match(self.regex_pattern, password):
            raise ValidationError("비밀번호가 유효하지 않습니다")

    def get_help_text(self):
        return "비밀번호는 문자, 숫자, 특수문자를 최소 하나씩 포함하여 8자리 이상 입력해야 합니다."


def validate_signup_info(data):
    """회원가입시에 입력한 데이터의 유효성을 검증합니다"""

    email_id = data.get("email_id")
    password1 = data.get("password1")
    password2 = data.get("password2")
    nickname = data.get("nickname")
    phone_number = data.get("phone_number")

    if not all([email_id, password1, password2, phone_number]):
        raise ValidationError("입력되지 않은 필수 입력 항목이 있습니다")

    if password1 != password2:
        raise ValidationError("비밀번호가 일치하지 않습니다")
    else:
        validate_password(password1)

    email = f"{email_id}@yourfan.com"
    if CustomUser.objects.filter(email=email).exists():
        raise ValidationError("이미 가입된 이메일입니다")

    if not SMSAuth.objects.filter(phone_number=phone_number).exists():
        raise ValidationError("인증되지 않은 휴대폰 번호입니다")

    return {
        "email": email,
        "password": password1,
        "nickname": nickname,
        "phone_number": phone_number,
    }


def validate_access_token(access_token):
    """액세스 토큰이 존재하는지 확인합니다"""
    if access_token is None:
        raise ValidationError("액세스 토큰이 존재하지 않습니다")


def validate_user_email(email, is_verified_email=False):
    """소셜 계정이 존재하는지, 그리고 유효한 계정인지를 확인합니다"""
    if email is None or is_verified_email is False:
        raise ValidationError("유효하지 않은 계정입니다")
