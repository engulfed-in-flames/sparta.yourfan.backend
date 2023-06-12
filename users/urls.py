from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("", views.UserList.as_view(), name="user_list"),
    path("signup/", views.UserList.as_view(), name="user_signup"),
    path("<int:pk>/", views.UserDetail.as_view(), name="=user_detail"),
    path("me/", views.Me.as_view(), name="me"),
    path("me/", views.Me.as_view(), name="withdrawal"),
    path("google-login/", views.google_auth),
    path("token/", views.CustomTokenObtainPairView.as_view(),
         name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("likes/<int:pk>/", views.UserLikes.as_view(), name="likes"),
]
