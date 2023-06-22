from rest_framework import serializers
from .models import Report


class CreateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"


class UpdateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"


class ReportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
