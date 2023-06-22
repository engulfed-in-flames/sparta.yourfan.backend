from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("", views.UserDetail.as_view(), name="user_list"),
    path("signup/", views.UserSignupView.as_view(), name="user_signup"),
    path("mail-valid/", views.UserSignupView.as_view()),
    path("<int:pk>/", views.UserDetail.as_view(), name="=user_detail"),
    path("me/", views.Me.as_view(), name="me"),
    path("kakao-login/", views.KakaoLogin.as_view()),
    path("github-login/", views.GithubLogin.as_view()),
    path("google-login/", views.GoogleLogin.as_view()),
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("likes/<int:pk>/", views.UserLikes.as_view(), name="likes"),
    path(
        "activate/<slug:uidb64>/<str:email>/",
        views.UserActivate.as_view(),
        name="activate",
    ),
    # path("dev/db/users/delete-all", views.DevUsersDeletedView.as_view(),),
]
