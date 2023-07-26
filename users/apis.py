import requests

from django.conf import settings
from rest_framework import exceptions

from users.models import CustomUser
from users.serializers import CustomTokenObtainPairSerializer
from users.validators import validate_access_token, validate_user_email

social_type = {
    "kakao": CustomUser.UserTypeChoices.KAKAO,
    "github": CustomUser.UserTypeChoices.GITHUB,
    "google": CustomUser.UserTypeChoices.GOOGLE,
}


def get_token_data(user):
    refresh_token = CustomTokenObtainPairSerializer.get_token(user)
    return {
        "refresh": str(refresh_token),
        "access": str(refresh_token.access_token),
    }


def create_social_type_user(email, nickname, avatar, type):
    user = CustomUser.objects.create_user(email=email)
    user.nickname = nickname or f"user#{user.pk}"
    user.avatar = avatar
    user.set_unusable_password()
    user.is_active = True
    user.user_type = social_type.get(type)
    user.save()

    return user


def get_user_data_from_kakao(code):
    url = "https://kauth.kakao.com/oauth/token"
    redirect_uri = settings.KAKAO_REDIRECT_URI
    response = requests.post(
        url=url,
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_API_KEY,
            "redirect_uri": redirect_uri,
            "code": code,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
        },
        headers={"Content-type": "application/x-www-form-urlencoded;charset=utf-8"},
    )
    access_token = response.json().get("access_token")

    url = "https://kapi.kakao.com/v2/user/me"
    response = requests.get(
        url=url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        },
    )
    user_data = response.json()
    kakao_account = user_data.get("kakao_account")
    profile = kakao_account.get("profile")
    user_email = kakao_account.get("email")
    is_verified_email = kakao_account.get("is_email_valid") and kakao_account.get(
        "is_email_verified"
    )
    validate_user_email(user_email, is_verified_email)

    return {
        "email": user_email,
        "nickname": profile.get("nickname", None),
        "avatar": profile.get("thumbnail_image_url", None),
    }


def get_user_data_from_github(code):
    url = "https://github.com/login/oauth/access_token"
    redirect_uri = settings.GH_REDIRECT_URI
    response = requests.post(
        url=url,
        data={
            "client_id": settings.GH_CLIENT_ID,
            "client_secret": settings.GH_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
        },
        headers={
            "Accept": "application/json",
        },
    )
    access_token = response.json().get("access_token")
    validate_access_token("access_token")
    url = "https://api.github.com/user"
    response = requests.get(
        url=url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )
    user_data = response.json()
    user_email = None
    url = "https://api.github.com/user/emails"
    response = requests.get(
        url=url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )
    user_emails_data = response.json()
    for email_data in user_emails_data:
        if email_data.get("primary") and email_data.get("verified"):
            user_email = email_data.get("email")
            validate_user_email(user_email, True)
    return {
        "email": user_email,
        "nickname": user_data.get("login", ""),
        "avatar": user_data.get("avatar_url", ""),
    }


def get_user_data_from_google(access_token):
    validate_access_token(access_token)

    url = "https://www.googleapis.com/oauth2/v2/userinfo"
    response = requests.get(
        url=url,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    user_data = response.json()
    user_email = user_data.get("email", None)
    is_verified_email = user_data.get("verified_email", False)
    user_nickname = user_data.get("name", None)
    user_avatar = user_data.get("picture", None)

    validate_user_email(user_email, is_verified_email)

    return {
        "email": user_email,
        "nickname": user_nickname or "",
        "avatar": user_avatar or "",
    }


method_type = {
    "kakao": get_user_data_from_kakao,
    "github": get_user_data_from_github,
    "google": get_user_data_from_google,
}


def get_or_create_social_user(access_token, social_type):
    validate_access_token(access_token)

    get_user_data = method_type.get(social_type)
    user_data = get_user_data(access_token)
    email, nickname, avatar = user_data.values()
    try:
        user = CustomUser.objects.get(email=email)
        if user.is_active == False:
            raise exceptions.ValidationError("비활성화된 계정입니다")
        return get_token_data(user)

    except CustomUser.DoesNotExist:
        user = create_social_type_user(
            email=email,
            nickname=nickname,
            avatar=avatar,
            type="kakao",
        )
        return get_token_data(user)
