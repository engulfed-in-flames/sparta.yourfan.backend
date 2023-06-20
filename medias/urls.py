from django.urls import path
from .views import UploadImage

urlpatterns = [
    path("upload-image/", UploadImage.as_view())
]
