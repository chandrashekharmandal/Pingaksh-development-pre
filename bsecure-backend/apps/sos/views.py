from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.permissions import IsVerifiedUser
from .models import SOSAlert, Incident, IncidentEvidence
from .serializers import (
    SOSAlertSerializer,
    SOSTriggerSerializer,
    IncidentSerializer,
    IncidentCreateSerializer,
)


class SOSTriggerView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request):
        serializer = SOSTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        booking = None
        if d.get("booking_id"):
            from apps.bookings.models import Booking

            try:
                booking = Booking.objects.get(id=d["booking_id"], user=request.user)
            except Booking.DoesNotExist:
                pass

        sos = SOSAlert.objects.create(
            user=request.user,
            booking=booking,
            trigger_method=d["trigger_method"],
            latitude=d["latitude"],
            longitude=d["longitude"],
        )

        # Count emergency contacts
        contacts_count = request.user.emergency_contacts.count()

        # Queue emergency contact alerts to Celery (fire-and-forget)
        try:
            from apps.sos.tasks import notify_emergency_contacts

            notify_emergency_contacts.delay(str(sos.id))
        except Exception:
            pass

        return Response(
            {
                "data": {
                    "sos_id": str(sos.id),
                    "status": sos.status,
                    "message": "SOS alert sent. Emergency contacts have been notified. Our control room has been alerted.",
                    "emergency_contacts_notified": contacts_count,
                    "triggered_at": sos.created_at.isoformat(),
                }
            }
        )


class SOSAlertListView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        alerts = SOSAlert.objects.filter(user=request.user).order_by("-created_at")
        return Response({"data": SOSAlertSerializer(alerts, many=True).data})


class SOSAlertDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            alert = SOSAlert.objects.get(id=pk)
        except SOSAlert.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "SOS alert not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        if alert.user != request.user and not request.user.is_staff:
            return Response(
                {"error": {"code": "FORBIDDEN", "message": "Access denied."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response({"data": SOSAlertSerializer(alert).data})


class IncidentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def get(self, request):
        incidents = Incident.objects.filter(filed_by=request.user).order_by(
            "-created_at"
        )
        return Response({"data": IncidentSerializer(incidents, many=True).data})

    def post(self, request):
        from apps.bookings.models import Booking

        serializer = IncidentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        try:
            booking = Booking.objects.get(id=d["booking_id"])
        except Booking.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Booking not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        incident = Incident.objects.create(
            booking=booking,
            filed_by=request.user,
            incident_type=d["incident_type"],
            severity=d["severity"],
            description=d["description"],
        )

        # Handle optional evidence files
        evidence_files = request.FILES.getlist("evidence_files", [])
        for f in evidence_files:
            file_type = "IMAGE" if f.content_type.startswith("image/") else "VIDEO"
            IncidentEvidence.objects.create(
                incident=incident,
                file=f,
                file_type=file_type,
            )

        return Response(
            {
                "data": {
                    "incident_id": str(incident.id),
                    "status": incident.status,
                    "message": "Incident report filed. Our team will review within 24 hours.",
                    "booking_id": str(booking.id),
                    "incident_type": incident.incident_type,
                    "evidence_count": len(evidence_files),
                }
            },
            status=status.HTTP_201_CREATED,
        )


class IncidentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            incident = Incident.objects.get(id=pk)
        except Incident.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Incident not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        if incident.filed_by != request.user and not request.user.is_staff:
            return Response(
                {"error": {"code": "FORBIDDEN", "message": "Access denied."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response({"data": IncidentSerializer(incident).data})
