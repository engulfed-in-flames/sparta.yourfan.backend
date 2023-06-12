from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Shorts
from .serializers import ShortsNotGetSerializer,ShortsGetSerializer
from .permissions import IsAdminOrIsUserMatch


class ShortModelViewset(viewsets.ModelViewSet):
    queryset = Shorts.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ShortsGetSerializer
        return ShortsNotGetSerializer
    
    def get_permissions(self):
        if self.action in ['destroy', 'partial_update']:
            permission_classes = [IsAdminOrIsUserMatch]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

            