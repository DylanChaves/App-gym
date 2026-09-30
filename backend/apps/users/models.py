from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models, transaction


class Role(models.Model):
    class Kind(models.TextChoices):
        ADMIN = "admin", "Administrador"
        COACH = "coach", "Entrenador"
        MEMBER = "member", "Cliente"

    slug = models.CharField(max_length=10, choices=Kind.choices, primary_key=True)

    def __str__(self):
        return self.get_slug_display()


class GymUserManager(UserManager):
    @transaction.atomic
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        user = super().create_superuser(username, email, password, **extra_fields)
        role, _ = Role.objects.get_or_create(slug=Role.Kind.ADMIN)
        user.roles.add(role)
        from apps.audit.models import AuditEvent

        AuditEvent.objects.create(
            actor=None,
            target=user,
            action="user.created",
            changes={"roles": ["admin"], "source": "bootstrap"},
        )
        return user


class User(AbstractUser):
    email = models.EmailField(unique=True)
    roles = models.ManyToManyField(Role, related_name="users", blank=True)
    objects = GymUserManager()
    REQUIRED_FIELDS = ["email"]

    def has_role(self, role):
        return self.is_active and self.roles.filter(slug=role).exists()


class CoachAssignment(models.Model):
    member = models.OneToOneField(User, on_delete=models.PROTECT, related_name="coach_assignment")
    coach = models.ForeignKey(User, on_delete=models.PROTECT, related_name="client_assignments")
    assigned_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="made_assignments")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(member=models.F("coach")), name="assignment_not_self"
            )
        ]
