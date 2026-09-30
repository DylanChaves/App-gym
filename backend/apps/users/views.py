import hashlib

from common.permissions import IsAdministrator
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from . import services
from .selectors import visible_users
from .serializers import (
    AssignmentSerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserReadSerializer,
    UserWriteSerializer,
)


def registration_ready():
    return bool(
        settings.REGISTRATION_ENABLED
        and settings.TERMS_VERSION
        and settings.PRIVACY_VERSION
        and settings.TERMS_URL
        and settings.PRIVACY_URL
    )


class AuthThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        # Do not put names or credentials in keys or logs; use the client address digest.
        digest = hashlib.sha256(self.get_ident(request).encode()).hexdigest()
        return self.cache_format % {"scope": self.scope, "ident": digest}


class RegistrationThrottle(AuthThrottle):
    scope = "registration"


class ConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                **settings.APP_CONFIG,
                "registration_enabled": registration_ready(),
                "terms_version": settings.TERMS_VERSION,
                "privacy_version": settings.PRIVACY_VERSION,
                "terms_url": settings.TERMS_URL,
                "privacy_url": settings.PRIVACY_URL,
            }
        )


class CsrfView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            return Response({"detail": "Usuario o contraseña incorrectos."}, status=400)
        login(request, user)
        return Response({"user": UserReadSerializer(user).data, "csrfToken": get_token(request)})


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(UserReadSerializer(request.user).data)


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationThrottle]

    def post(self, request):
        if not registration_ready():
            raise PermissionDenied(
                "El autorregistro aún no está habilitado. Contacta al administrador."
            )
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserReadSerializer(user).data, status=201)


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_permissions(self):
        if self.action in ["create", "partial_update", "assign_coach"]:
            return [IsAdministrator()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = visible_users(self.request.user)
        role = self.request.query_params.get("role")
        if role in ["admin", "coach", "member"]:
            queryset = queryset.filter(roles__slug=role)
        if self.request.query_params.get("assigned") == "me":
            queryset = queryset.filter(coach_assignment__coach=self.request.user)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return UserWriteSerializer
        return UserReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(UserReadSerializer(serializer.save()).data, status=201)

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(UserReadSerializer(serializer.save()).data)

    @action(detail=True, methods=["post"], url_path="coach")
    def assign_coach(self, request, pk=None):
        member = self.get_object()
        serializer = AssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = services.assign_coach(
            request.user, member.pk, serializer.validated_data["coach_id"]
        )
        return Response(UserReadSerializer(member).data)
