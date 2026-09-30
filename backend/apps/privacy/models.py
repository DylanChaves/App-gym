from django.conf import settings
from django.db import models


class PolicyAcceptance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    kind = models.CharField(
        max_length=10, choices=[("terms", "Contrato"), ("privacy", "Privacidad")]
    )
    version = models.CharField(max_length=100)
    accepted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "kind", "version"], name="unique_acceptance")
        ]
