from rest_framework.permissions import BasePermission


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_role("admin")
