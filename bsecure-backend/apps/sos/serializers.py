from rest_framework import serializers
from .models import SOSAlert, Incident, IncidentEvidence


class SOSAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSAlert
        fields = [
            "id",
            "trigger_method",
            "status",
            "latitude",
            "longitude",
            "acknowledged_at",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = fields


class SOSTriggerSerializer(serializers.Serializer):
    trigger_method = serializers.ChoiceField(choices=SOSAlert.TRIGGER_METHOD_CHOICES)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    booking_id = serializers.UUIDField(required=False, allow_null=True)


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = [
            "id",
            "incident_type",
            "severity",
            "description",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]


class IncidentCreateSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()
    incident_type = serializers.ChoiceField(choices=Incident.INCIDENT_TYPE_CHOICES)
    severity = serializers.ChoiceField(
        choices=Incident.SEVERITY_CHOICES, default="MEDIUM"
    )
    description = serializers.CharField(max_length=2000)
