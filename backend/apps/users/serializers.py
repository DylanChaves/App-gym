from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from apps.privacy.models import PolicyAcceptance

from . import services
from .models import CoachAssignment, Role, User


class StrictSerializerMixin:
    def to_internal_value(self, data):
        unknown = set(data) - {key for key, field in self.fields.items() if not field.read_only}
        if unknown:
            raise serializers.ValidationError({key: "Campo no permitido." for key in unknown})
        return super().to_internal_value(data)


class UserReadSerializer(serializers.ModelSerializer):
    roles = serializers.SlugRelatedField(slug_field="slug", many=True, read_only=True)
    coach_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "roles",
            "is_active",
            "coach_id",
        ]

    def get_coach_id(self, obj):
        try:
            return obj.coach_assignment.coach_id
        except CoachAssignment.DoesNotExist:
            return None


class UserWriteSerializer(StrictSerializerMixin, serializers.ModelSerializer):
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=Role.Kind.values), allow_empty=False
    )
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active", "roles", "password"]

    def validate(self, attrs):
        if self.instance and "password" in attrs:
            raise serializers.ValidationError(
                {"password": "El cambio de contraseña requiere un flujo separado."}
            )
        if not self.instance:
            if not attrs.get("password"):
                raise serializers.ValidationError(
                    {"password": "Se requiere una contraseña inicial."}
                )
            candidate = User(
                **{key: value for key, value in attrs.items() if key not in ["roles", "password"]}
            )
            try:
                validate_password(attrs["password"], candidate)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({"password": exc.messages}) from exc
        return attrs

    def create(self, validated_data):
        return services.create_user(self.context["request"].user, validated_data)

    def update(self, instance, validated_data):
        return services.update_user(self.context["request"].user, instance, validated_data)


class LoginSerializer(StrictSerializerMixin, serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=256)


class AssignmentSerializer(StrictSerializerMixin, serializers.Serializer):
    coach_id = serializers.IntegerField(allow_null=True, min_value=1)


class RegistrationSerializer(StrictSerializerMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=256)
    terms_version = serializers.CharField(write_only=True)
    privacy_version = serializers.CharField(write_only=True)
    accept_terms = serializers.BooleanField(write_only=True)
    accept_privacy = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "terms_version",
            "privacy_version",
            "accept_terms",
            "accept_privacy",
        ]

    def validate(self, attrs):
        if not attrs["accept_terms"] or not attrs["accept_privacy"]:
            raise serializers.ValidationError("Confirma cada elección requerida por separado.")
        if (
            attrs["terms_version"] != settings.TERMS_VERSION
            or attrs["privacy_version"] != settings.PRIVACY_VERSION
        ):
            raise serializers.ValidationError(
                "Consulta las versiones vigentes antes de registrarte."
            )
        try:
            validate_password(
                attrs["password"], User(username=attrs["username"], email=attrs["email"])
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from exc
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        for field in ["terms_version", "privacy_version", "accept_terms", "accept_privacy"]:
            validated_data.pop(field)
        user = services.create_user(None, {**validated_data, "roles": ["member"]})
        for kind, version in [
            ("terms", settings.TERMS_VERSION),
            ("privacy", settings.PRIVACY_VERSION),
        ]:
            PolicyAcceptance.objects.create(user=user, kind=kind, version=version)
        return user
