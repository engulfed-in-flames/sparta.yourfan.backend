from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import status
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from users import serializers
from users.apis import get_or_create_social_user
from users.models import CustomUser, SMSAuth
from users.validators import validate_signup_info


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

        return Response(status=status.HTTP_200_OK)


class SendSMSView(APIView):
    """네이버 클라우드의 SMS API를 사용하여 클라이언트에게 인증 번호를 전송"""

    def get(self, request):
        sms_auth_list = SMSAuth.objects.all()
        serializer = serializers.SMSAuthSerializer(
            sms_auth_list,
            many=True,
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        phone_number = str(request.data.get("phone_number", None))
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"message": "이미 사용된 휴대폰 번호입니다"},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        try:
            inst, _ = SMSAuth.objects.get_or_create(phone_number=phone_number)
            inst.send_sms()
            return Response(status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"message": "휴대폰 번호가 유효하지 않습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserDetail(APIView):
    """특정 유저 정보 조회"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(CustomUser, pk=pk)

    def get(self, request, pk):
        if request.user == user or request.user.is_staff:
            user = self.get_object(pk)
            serializer = serializers.UserDetailSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class Me(APIView):
    """마이프로필 페이지에서 CRUD를 수행합니다"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
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

    def delete(self, request):
        """회원 탈퇴"""
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class User(APIView):
    def get(self, request):
        if request.user.is_admin:
            users = CustomUser.objects.all()
            serializer = serializers.UserSerializer(users, many=True)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class Signup(APIView):
    def post(self, request):
        """회원 가입"""
        serializer = serializers.CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class KakaoLogin(APIView):
    def post(self, request):
        """리퀘스트 데이터로 카카오 API 액세스 토큰을 받아 깃허브 로그인을 시도하고, 유저 액세스 토큰을 반환합니다"""
        code = request.data.get("code")
        try:
            token_data = get_or_create_social_user(code, "kakao")
            return Response(
                data=token_data,
                status=status.HTTP_200_OK,
            )

        except exceptions.ValidationError as err:
            error_message = err.args[0]
            return Response(
                data={"error_message": error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GithubLogin(APIView):
    def post(self, request):
        """리퀘스트 데이터로 깃허브 API 액세스 토큰을 받아 깃허브 로그인을 시도하고, 유저 액세스 토큰을 반환합니다"""
        code = request.data.get("code", None)
        try:
            token_data = get_or_create_social_user(code, "github")
            return Response(
                data=token_data,
                status=status.HTTP_200_OK,
            )

        except exceptions.ValidationError as err:
            return Response(
                data={"error_message": str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GoogleLogin(APIView):
    def post(self, request):
        """리퀘스트 데이터로 구글 API 액세스 토큰을 받아 구글 로그인을 시도하고, 유저 액세스 토큰을 반환합니다"""
        access_token = request.data.get("access_token", None)
        try:
            token_data = get_or_create_social_user(access_token, "google")
            return Response(
                data=token_data,
                status=status.HTTP_200_OK,
            )

        except exceptions.ValidationError as err:
            return Response(
                data={"error_message": str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )
