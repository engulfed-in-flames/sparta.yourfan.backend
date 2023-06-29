import requests

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings
from django.contrib.auth.password_validation import validate_password

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from . import serializers
from .models import CustomUser, SMSAuth


"""user 테이블 초기화
아래의 두 코드를 활성화시키면, user 인스턴스가 모두 삭제됩니다.

user = CustomUser.objects.all()
user.delete()
"""


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer


class CompareSMSAuthNumberView(APIView):
    """클라이언트가 입력한 인증 번호를 DB상의 인증 번호와 비교"""

    def post(self, request):
        phone_number = request.data.get("phone_number", None)
        auth_number_entered = request.data.get("auth_number", None)
        result = SMSAuth.compare_auth_number(
            phone_number=phone_number,
            auth_number=auth_number_entered,
        )
        if not result:
            return Response(
                {"message": "인증 번호가 일치하지 않습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = CustomUser.objects.filter(phone_number=phone_number)
        if user.exists():
            return Response(
                {"message": "이미 사용된 번호입니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_200_OK)


class SendSMSView(APIView):
    """네이버 클라우드의 SMS API를 사용하여 클라이언트에게 인증 번호를 전송"""

    def post(self, request):
        phone_number = str(request.data.get("phone_number", None))
        try:
            inst, _ = SMSAuth.objects.get_or_create(phone_number=phone_number)
            inst.send_sms()
            return Response(status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"message": err}, status=status.HTTP_400_BAD_REQUEST)


class UserList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user_list = CustomUser.objects.all()
        serializer = serializers.UserSerializer(
            instance=user_list,
            many=True,
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class UserDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(CustomUser, pk=pk)

    def get(self, request, pk):
        """특정 유저 조회"""
        user = self.get_object(pk)
        serializer = serializers.UserDetailSerializer(user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        """(관리자 권한 필요) 특정 유저 삭제
        커스텀 퍼미션 클래스는 현재 정의 중이므로, 임시로 코드를 작성
        """
        request_user = request.user
        if request_user.is_admin or request_user.is_staff:
            target_user = CustomUser.objects.get(pk=pk)
            target_user.is_active = False
            target_user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """내 정보 조회"""
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
        serializer = serializers.UpdateUserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # def patch(self, request):
    #     """비밀번호 변경"""
    #     serializer = serializers.UpdatePasswordSerializer(
    #         request.user,
    #         data=request.data,
    #         partial=True,
    #     )
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(status=status.HTTP_200_OK)
    #     else:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """회원 탈퇴"""
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignupView(APIView):
    def post(self, request):
        """회원 가입"""
        verified = request.data.get("verified", None)
        if not verified:
            return Response(
                {"message": "인증이 필요합니다"}, status=status.HTTP_400_BAD_REQUEST
            )

        password1 = request.data.get("password1", None)
        password2 = request.data.get("password2", None)
        condition1 = all([password1, password2])
        condition2 = password1 == password2
        if not all([condition1, condition2]):
            return Response(
                {"message": "비밀번호가 일치하지 않습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            validate_password(password1)
        except:
            return Response(
                {"message": "비밀번호가 유효하지 않습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_id = request.data.get("email_id")
        email = f"{email_id}@yourfan.com"
        if CustomUser.objects.filter(email=email).exists():
            return Response(
                {"message": "이미 가입했거나 휴면 처리된 계정입니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        nickname = request.data.get("nickname", None)
        data = {
            "email": email,
            "password": password1,
            "nickname": nickname,
        }
        serializer = serializers.ConvertSignupDataSerializer(data=data)
        if serializer.is_valid():
            data = serializer.validated_data
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = serializers.CreateUserSerializer(data=data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    serializer.save()
                    return Response(status=status.HTTP_201_CREATED)
            except Exception as err:
                return Response(
                    err,
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


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
