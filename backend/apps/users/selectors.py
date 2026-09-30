from django.db.models import Q

from .models import User


def visible_users(user):
    queryset = User.objects.prefetch_related("roles").select_related("coach_assignment__coach")
    if user.has_role("admin"):
        return queryset.order_by("id")
    scope = Q(pk=user.pk)
    if user.has_role("coach"):
        scope |= Q(coach_assignment__coach=user, roles__slug="member")
    return queryset.filter(scope).distinct().order_by("id")
