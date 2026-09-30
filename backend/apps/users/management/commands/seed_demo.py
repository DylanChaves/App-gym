import json
import secrets

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.users.models import User
from apps.users.services import assign_coach, create_user


class Command(BaseCommand):
    help = "Crea cuentas ficticias locales sin modificar cuentas existentes."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Disponible únicamente en desarrollo con DEBUG=true.")
        destination = settings.BASE_DIR.parent / ".local" / "demo-credentials.json"
        specs = [
            ("demo_admin", ["admin", "coach"], "Administración demo"),
            ("demo_coach", ["coach"], "Entrenador demo"),
            ("demo_member", ["member"], "Cliente asignado demo"),
            ("demo_other", ["member"], "Cliente sin asignar demo"),
        ]
        existing = User.objects.filter(username__in=[name for name, _, _ in specs]).count()
        if existing:
            if destination.exists() and existing == len(specs):
                self.stdout.write(
                    "Las cuentas demo ya existen. Consulta .local/demo-credentials.json."
                )
                return
            raise CommandError(
                "Existen cuentas con nombres demo. No se sobrescriben ni se cambian contraseñas."
            )
        accounts = {}
        created = {}
        for name, roles, label in specs:
            password = secrets.token_urlsafe(24)
            user = create_user(
                created.get("demo_admin"),
                {
                    "username": name,
                    "email": f"{name}@example.test",
                    "first_name": label,
                    "password": password,
                    "roles": roles,
                },
            )
            created[name] = user
            accounts[name] = {"username": name, "password": password, "id": user.pk}
        assign_coach(created["demo_admin"], created["demo_member"].pk, created["demo_coach"].pk)
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(json.dumps(accounts, indent=2), encoding="utf-8")
        self.stdout.write(
            "Cuentas ficticias creadas. Credenciales privadas en .local/demo-credentials.json."
        )
