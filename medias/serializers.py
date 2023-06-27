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
        fields = (
            "pk",
            "user",
            "title",
            "content",
            "image_title",
            "image_url",
            "cloudflare_image_id",
            "created_at",
            "updated_at",
        )
