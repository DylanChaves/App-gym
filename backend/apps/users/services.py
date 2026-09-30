from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.audit.models import AuditEvent

from .models import CoachAssignment, Role, User


def audit(actor, target, action, changes):
    AuditEvent.objects.create(actor=actor, target=target, action=action, changes=changes)


@transaction.atomic
def create_user(actor, validated):
    roles = validated.pop("roles")
    password = validated.pop("password")
    user = User.objects.create_user(password=password, **validated)
    user.roles.set(Role.objects.filter(slug__in=roles))
    audit(actor, user, "user.created", {"roles": sorted(roles)})
    return user


@transaction.atomic
def update_user(actor, instance, validated):
    # Serialize administrative mutations to preserve the last active administrator.
    list(User.objects.select_for_update().order_by("id").values_list("id", flat=True))
    instance = User.objects.get(pk=instance.pk)
    before = sorted(instance.roles.values_list("slug", flat=True))
    after = sorted(validated.pop("roles", before))
    active_after = validated.get("is_active", instance.is_active)
    if instance.has_role("admin") and ("admin" not in after or not active_after):
        others = User.objects.filter(is_active=True, roles__slug="admin").exclude(pk=instance.pk)
        if not others.exists():
            raise ValidationError({"roles": "Debe conservarse al menos un administrador activo."})
    if ("coach" not in after or not active_after) and instance.client_assignments.exists():
        raise ValidationError(
            {"roles": "Reasigna los clientes antes de quitar o desactivar al entrenador."}
        )
    if "member" not in after and CoachAssignment.objects.filter(member=instance).exists():
        raise ValidationError({"roles": "Retira la asignación antes de quitar el rol de cliente."})
    active_before = instance.is_active
    for field, value in validated.items():
        setattr(instance, field, value)
    instance.save()
    instance.roles.set(Role.objects.filter(slug__in=after))
    if before != after:
        audit(actor, instance, "roles.changed", {"before": before, "after": after})
    if active_before != active_after:
        audit(actor, instance, "user.status_changed", {"active": active_after})
    return instance


@transaction.atomic
def assign_coach(actor, member_id, coach_id):
    # Same lock order as role changes, so concurrent changes cannot leave invalid assignments.
    users = list(
        User.objects.select_for_update()
        .filter(pk__in=[member_id, coach_id] if coach_id else [member_id])
        .order_by("id")
    )
    indexed = {user.pk: user for user in users}
    member = indexed.get(member_id)
    coach = indexed.get(coach_id)
    if not member or not member.has_role("member"):
        raise ValidationError({"member": "Se requiere un cliente activo."})
    if coach_id and (not coach or not coach.has_role("coach") or coach_id == member_id):
        raise ValidationError(
            {"coach_id": "Selecciona un entrenador activo diferente del cliente."}
        )
    previous = CoachAssignment.objects.filter(member=member).first()
    before = previous.coach_id if previous else None
    if coach_id:
        CoachAssignment.objects.update_or_create(
            member=member, defaults={"coach": coach, "assigned_by": actor}
        )
    elif previous:
        previous.delete()
    if before != coach_id:
        audit(actor, member, "assignment.changed", {"before": before, "after": coach_id})
    return member
