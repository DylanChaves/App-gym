from common.permissions import IsAdministrator
from django.urls import path
from rest_framework import generics, serializers

from .models import AuditEvent


class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = ["id", "actor_id", "target_id", "action", "changes", "created_at"]


class AuditListView(generics.ListAPIView):
    permission_classes = [IsAdministrator]
    serializer_class = AuditSerializer
    queryset = AuditEvent.objects.all()


urlpatterns = [path("", AuditListView.as_view())]
