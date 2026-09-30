from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name="audit_actions"
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="audit_events"
    )
    action = models.CharField(max_length=50)
    changes = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
