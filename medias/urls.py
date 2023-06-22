from django.urls import path
from . import views

urlpatterns = [
    path("upload-image/", views.UploadImage.as_view()),
    path("report/", views.ReportList.as_view()),
    path("report/<int:pk>/", views.ReportDetail.as_view()),
]
