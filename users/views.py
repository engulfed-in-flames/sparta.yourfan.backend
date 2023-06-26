import requests

from django.shortcuts import get_object_or_404, render
from django.db import transaction
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.views import TokenObtainPairView

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from .models import CustomUser
from . import serializers
import traceback

# db 삭제 귀찮을 시 그냥 아래 2줄 활성화 시켜, user를 삭제하세요
# user = CustomUser.objects.all()
# user.delete()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer


# class DevUsersDeletedView(APIView):
#     """개발용 User DB 전체 삭제, ##사용시 주의##"""
#     def get(self, request):
#         user = CustomUser.objects.all()
#         user.delete()
#         return Response({"msg":"Users_all_deleted"},status=status.HTTP_200_OK)


class UserActivate(APIView):
    """이메일 인증"""

    def get(self, request, uidb64, email):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(CustomUser, pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        try:
            if user is not None and user.email:
                user.is_active = True
                user.save()
                return render(request, "conform.html")
            else:
                return Response(
                    status=status.HTTP_408_REQUEST_TIMEOUT,
                )

        except Exception as e:
            print(traceback.format_exc())


class UserSignupView(APIView):
    def post(self, request):
        """회원 가입"""
        try:
            email = request.data.get("email")
            if CustomUser.objects.filter(email=email).exists():
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                raise NotFound
        except NotFound:
            serializer = serializers.CreateUserSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        serializer.save()
                        return Response(status=status.HTTP_200_OK)
                except Exception:
                    return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )


class UserDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        """유저 오브젝트 가져오기"""
        return get_object_or_404(CustomUser, pk=pk)

    def get(self, request, pk=None):
        if pk is None:
            """전체유저 조회"""
            users = CustomUser.objects.all()
            serializer = serializers.UserSerializer(users, many=True)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            """특정 유저 조회"""
            user = self.get_object(pk)
            serializer = serializers.UserDetailSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )


class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """내 정보 보기"""
        user = request.user
        if user:
            serializer = serializers.UserDetailSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        """내 정보 수정"""
        user = get_object_or_404(CustomUser, id=request.user.id)
        serializer = serializers.UpdateUserSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """비밀번호 변경"""
        user = request.user
        data = request.data
        serializer = serializers.UpdatePasswordSerializer(user, data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    serializer = serializers.UserSerializer(user)
                    return Response(
                        serializer.data,
                        status=status.HTTP_200_OK,
                    )
            except Exception:
                raise ValueError("비밀번호 변경에 실패했습니다.")
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request):
        """회원 탈퇴"""
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_200_OK)


class KakaoLogin(APIView):
    def post(self, request):
        """카카오 로그인"""
        code = request.data.get("code", None)
        token_url = f"https://kauth.kakao.com/oauth/token"

        redirect_uri = settings.KAKAO_REDIRECT_URI

        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = requests.post(
            token_url,
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
        user_url = "https://kapi.kakao.com/v2/user/me"
        response = requests.get(
            user_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )
        user_data = response.json()
        kakao_account = user_data.get("kakao_account")
        profile = kakao_account.get("profile")

        if not kakao_account.get("is_email_valid") and not kakao_account.get(
            "is_email_verified"
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_email = kakao_account.get("email")

        try:
            user = CustomUser.objects.get(email=user_email)

            if user.is_active == False:
                return Response(status=status.HTTP_403_NOT_ACCEPTABLE)

            refresh_token = serializers.CustomTokenObtainPairSerializer.get_token(user)
            return Response(
                data={
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                },
                status=status.HTTP_200_OK,
            )

        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create_user(email=user_email)
            user.set_unusable_password()
            user.nickname = profile.get("nickname", f"user#{user.pk}")
            user.avatar = profile.get("thumbnail_image_url", None)
            user.is_active = True
            user.user_type = CustomUser.UserTypeChoices.KAKAO
            user.save()

            refresh_token = serializers.CustomTokenObtainPairSerializer.get_token(user)

            return Response(
                data={
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                },
                status=status.HTTP_200_OK,
            )


class GithubLogin(APIView):
    def post(self, request):
        """깃헙 로그인"""
        code = request.data.get("code", None)
        token_url = "https://github.com/login/oauth/access_token"

        redirect_uri = settings.GH_REDIRECT_URI

        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = requests.post(
            token_url,
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
        user_url = "https://api.github.com/user"
        user_email_url = "https://api.github.com/user/emails"

        response = requests.get(
            user_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        user_data = response.json()
        response = requests.get(
            user_email_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        user_emails = response.json()

        user_email = None
        for email_data in user_emails:
            if email_data.get("primary") and email_data.get("verified"):
                user_email = email_data.get("email")

        try:
            user = CustomUser.objects.get(email=user_email)

            if user.is_active == False:
                return Response(status=status.HTTP_403_FORBIDDEN)

            refresh_token = serializers.CustomTokenObtainPairSerializer.get_token(user)

            return Response(
                data={
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                },
                status=status.HTTP_200_OK,
            )

        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create_user(email=user_email)
            user.nickname = user_data.get("login", f"user#{user.pk}")
            user.avatar = user_data.get("avatar_url", None)
            user.set_unusable_password()
            user.is_active = True
            user.user_type = CustomUser.UserTypeChoices.GITHUB
            user.save()

            refresh_token = serializers.CustomTokenObtainPairSerializer.get_token(user)

            return Response(
                data={
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                },
                status=status.HTTP_200_OK,
            )


class GoogleLogin(APIView):
    def post(self, request):
        """구글 로그인"""
        access_token = request.data.get("access_token", None)
        token_url = "https://www.googleapis.com/oauth2/v2/userinfo"

        if access_token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = requests.get(
            token_url,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        user_data = response.json()
        user_email = user_data.get("email", None)
        is_verified_email = user_data.get("verified_email", False)
        user_nickname = user_data.get("name", None)
        user_avatar = user_data.get("picture", None)

        if user_email is None or is_verified_email is False:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=user_email)

            if user.is_active == False:
                return Response(status=status.HTTP_403_FORBIDDEN)

            refresh_token = serializers.CustomTokenObtainPairSerializer.get_token(user)

            return Response(
                data={
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                },
                status=status.HTTP_200_OK,
            )

        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create_user(email=user_email)

            user.nickname = (
                user_nickname if user_nickname is not None else f"user#{user.pk}"
            )
            user.avatar = user_avatar
            user.set_unusable_password()
            user.is_active = True
            user.user_type = CustomUser.UserTypeChoices.GOOGLE
            user.save()

            refresh_token = serializers.CustomTokenObtainPairSerializer.get_token(user)

            return Response(
                data={
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                },
                status=status.HTTP_200_OK,
            )
