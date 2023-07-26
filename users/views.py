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

    def delete(self, request):
        """회원 탈퇴"""
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignupView(APIView):
    def post(self, request):
        """회원 가입"""
        email_id = request.data.get("email_id")
        password1 = request.data.get("password1", None)
        password2 = request.data.get("password2", None)
        nickname = request.data.get("nickname", None)
        phone_number = request.data.get("phone_number", None)

        data = validate_signup_info(
            email_id=email_id,
            password1=password1,
            password2=password2,
            nickname=nickname,
            phone_number=phone_number,
        )

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
        """리퀘스트 데이터로 카카오 API 액세스 토큰을 받아 깃허브 로그인을 시도하고, 유저 액세스 토큰을 반환합니다"""
        code = request.data.get("code")
        try:
            token_data = get_or_create_social_user(code, "kakao")
            return Response(
                data=token_data,
                status=status.HTTP_200_OK,
            )

        except exceptions.ValidationError as err:
            return Response(
                data={"error_message": str(err)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # code = request.data.get("code")
        # token_url = f"https://kauth.kakao.com/oauth/token"

        # redirect_uri = settings.KAKAO_REDIRECT_URI

        # if code is None:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        # response = requests.post(
        #     token_url,
        #     data={
        #         "grant_type": "authorization_code",
        #         "client_id": settings.KAKAO_API_KEY,
        #         "redirect_uri": redirect_uri,
        #         "code": code,
        #         "client_secret": settings.KAKAO_CLIENT_SECRET,
        #     },
        #     headers={"Content-type": "application/x-www-form-urlencoded;charset=utf-8"},
        # )

        # access_token = response.json().get("access_token")
        # user_url = "https://kapi.kakao.com/v2/user/me"
        # response = requests.get(
        #     user_url,
        #     headers={
        #         "Authorization": f"Bearer {access_token}",
        #         "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        #     },
        # )
        # user_data = response.json()
        # kakao_account = user_data.get("kakao_account")
        # profile = kakao_account.get("profile")
        # is_verified_email = kakao_account.get("is_email_valid") and kakao_account.get(
        #     "is_email_verified"
        # )
        # if not kakao_account.get("is_email_valid") and not kakao_account.get(
        #     "is_email_verified"
        # ):
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        # user_email = kakao_account.get("email")

        # try:
        #     user = CustomUser.objects.get(email=user_email)

        #     if user.is_active == False:
        #         return Response(status=status.HTTP_403_NOT_ACCEPTABLE)

        #     refresh_token = serializers.CustomTokenObtainPairSerializer.get_token(user)
        #     return Response(
        #         data={
        #             "refresh": str(refresh_token),
        #             "access": str(refresh_token.access_token),
        #         },
        #         status=status.HTTP_200_OK,
        #     )

        # except CustomUser.DoesNotExist:
        #     user = CustomUser.objects.create_user(email=user_email)
        #     user.set_unusable_password()
        #     user.nickname = profile.get("nickname", f"user#{user.pk}")
        #     user.avatar = profile.get("thumbnail_image_url", None)
        #     user.is_active = True
        #     user.user_type = CustomUser.UserTypeChoices.KAKAO
        #     user.save()

        #     refresh_token = serializers.CustomTokenObtainPairSerializer.get_token(user)

        #     return Response(
        #         data={
        #             "refresh": str(refresh_token),
        #             "access": str(refresh_token.access_token),
        #         },
        #         status=status.HTTP_200_OK,
        #     )


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
