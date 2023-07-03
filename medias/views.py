import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .models import Report
from . import serializers


class UploadImage(APIView):
    def post(self, request):
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ACCOUNT_ID}/images/v2/direct_upload"
        one_time_url = requests.post(
            url, headers={"Authorization": f"Bearer {settings.CF_API_TOKEN}"}
        )
        one_time_url = one_time_url.json()
        result = one_time_url.get("result")
        return Response({"uploadURL": result.get("uploadURL")})


class ReportList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        ReportList = Report.objects.all()
        serializer = serializers.ReportSerializer(
            ReportList,
            many=True,
        )
        return Response(
            serializer.data,
            status=HTTP_200_OK,
        )

    def post(self, request):
        serializer = serializers.CreateReportSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.save(user=request.user)
            serializer = serializers.ReportDetailSerializer(report)
            return Response(
                serializer.data,
                status=HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )


class ReportDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Report, pk=pk)

    def get(self, request, pk):
        report = self.get_object(pk)
        serializer = serializers.ReportDetailSerializer(report)
        return Response(serializer.data, status=HTTP_200_OK)

    def put(self, request, pk):
        report = self.get_object(pk)

        if report.user != request.user:
            return Response(status=HTTP_400_BAD_REQUEST)

        print(request.data)
        serializer = serializers.UpdateReportSerializer(
            report,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            report = serializer.save()
            serializer = serializers.ReportDetailSerializer(report)
            return Response(
                serializer.data,
                status=HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
        report = self.get_object(pk)

        if report.user != request.user:
            return Response(status=HTTP_400_BAD_REQUEST)

        report.delete()
        return Response(status=HTTP_200_OK)
