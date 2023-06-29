from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("", views.UserList.as_view(), name="user_list"),
    path("<int:pk>/", views.UserDetail.as_view(), name="user_detail"),
    path("me/", views.Me.as_view(), name="me"),
    path("signup/", views.SignupView.as_view(), name="user_signup"),
    path("sms-auth/", views.SendSMSView.as_view(), name="sms-auth"),
    path(
        "sms-auth-number/",
        views.CompareSMSAuthNumberView.as_view(),
        name="sms-auth-number",
    ),
    path("kakao-login/", views.KakaoLogin.as_view()),
    path("github-login/", views.GithubLogin.as_view()),
    path("google-login/", views.GoogleLogin.as_view()),
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
