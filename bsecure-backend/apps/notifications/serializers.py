from rest_framework import serializers
from .models import NotificationLog, NotificationPreference


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = [
            "id",
            "notification_type",
            "title",
            "body",
            "data",
            "channel",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "push_enabled",
            "sms_enabled",
            "email_enabled",
            "marketing_push",
            "marketing_email",
        ]
