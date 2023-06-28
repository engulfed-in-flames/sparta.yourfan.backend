import re
from django.core.exceptions import ValidationError


class PasswordFormatValidator:
    def __init__(self):
        self.regex_pattern = r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@#$%^&+=]).+$"

    def validate(self, password, user=None):
        if not re.match(self.regex_pattern, password):
            raise ValidationError(code="password_invalid_format")

    def get_help_text(self):
        return "비밀번호는 문자, 숫자, 특수문자를 최소 하나씩 포함하여 8자리 이상 입력해야 합니다."
