import re

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from rest_framework.response import Response

from .models import CustomUser, SMSAuth


class PasswordFormatValidator:
    def __init__(self):
        self.regex_pattern = (
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$"
        )

    def validate(self, password, user=None):
        if not re.match(self.regex_pattern, password):
            raise ValidationError(code="password_invalid_format")

    def get_help_text(self):
        return "비밀번호는 문자, 숫자, 특수문자를 최소 하나씩 포함하여 8자리 이상 입력해야 합니다."


def validate_signup_info(email_id, password1, password2, nickname, phone_number):
    """회원가입시에 입력한 정보를 검증합니다"""
    # 비밀번호 검증
    try:
        condition1 = all([password1, password2])
        condition2 = password1 == password2
        if not all([condition1, condition2]):
            raise ValidationError
        validate_password(password1)
    except:
        return Response(
            {"message": "비밀번호가 유효하지 않습니다"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 계정 존재 유무 확인
    email = f"{email_id}@yourfan.com"
    if CustomUser.objects.filter(email=email).exists():
        return Response(
            {"message": "이미 가입한 회원입니다"},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )

    # 휴대폰 번호 유무 확인
    if phone_number is None:
        return Response(
            {"message": "휴대폰 번호를 입력하세요"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 휴대폰 인증 유무 확인
    if not SMSAuth.objects.filter(phone_number=phone_number).exists():
        return Response(
            {"message": "인증되지 않은 휴대폰 번호입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = {
        "email": email,
        "password": password1,
        "nickname": nickname,
        "phone_number": phone_number,
    }
    return data
