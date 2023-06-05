from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("", views.UserList.as_view(), name="user_list"),
    path("<int:pk>/", views.UserDetail.as_view(), name="=user_detail"),
    path("me/", views.Me.as_view(), name="me"),
    path("github-login/", views.GithubLogin.as_view()),
    path("kakako-login/", views.KaKaoLogin.as_view()),
    path("google-login/", views.GoogleLogin.as_view()),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
