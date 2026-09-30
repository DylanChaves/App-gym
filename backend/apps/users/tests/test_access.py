from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from apps.audit.models import AuditEvent
from apps.privacy.models import PolicyAcceptance
from apps.users.models import CoachAssignment, Role, User
from apps.users.services import assign_coach


class AccessTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        for role in Role.Kind.values:
            Role.objects.get_or_create(slug=role)
        cls.admin = cls.make_user("administrator", ["admin"])
        cls.coach = cls.make_user("coach_one", ["coach"])
        cls.coach2 = cls.make_user("coach_two", ["coach"])
        cls.member = cls.make_user("member_one", ["member"])
        cls.other = cls.make_user("member_two", ["member"])
        assign_coach(cls.admin, cls.member.pk, cls.coach.pk)
        assign_coach(cls.admin, cls.other.pk, cls.coach2.pk)

    @staticmethod
    def make_user(name, roles):
        user = User.objects.create_user(
            username=name, email=f"{name}@example.test", password="TestOnly!Pass2384"
        )
        user.roles.set(Role.objects.filter(slug__in=roles))
        return user

    def setUp(self):
        cache.clear()

    def login_as(self, user):
        self.client.force_login(user)

    def test_real_login_me_logout_and_session_invalidation(self):
        response = self.client.post(
            "/api/auth/login/", {"username": self.member.username, "password": "TestOnly!Pass2384"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["id"], self.member.pk)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, 204)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 403)

    def test_invalid_password_and_inactive_account(self):
        for username in [self.member.username, "absent"]:
            response = self.client.post(
                "/api/auth/login/", {"username": username, "password": "wrong"}
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data["detail"], "Usuario o contraseña incorrectos.")
        self.member.is_active = False
        self.member.save()
        response = self.client.post(
            "/api/auth/login/", {"username": self.member.username, "password": "TestOnly!Pass2384"}
        )
        self.assertEqual(response.status_code, 400)

    def test_csrf_required_on_login_and_logout(self):
        client = APIClient(enforce_csrf_checks=True)
        payload = {"username": self.member.username, "password": "TestOnly!Pass2384"}
        self.assertEqual(client.post("/api/auth/login/", payload).status_code, 403)
        csrf = client.get("/api/auth/csrf/").data["csrfToken"]
        response = client.post("/api/auth/login/", payload, HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.post("/api/auth/logout/").status_code, 403)
        self.assertEqual(
            client.post(
                "/api/auth/logout/", HTTP_X_CSRFTOKEN=response.data["csrfToken"]
            ).status_code,
            204,
        )

    def test_anonymous_cannot_read_users(self):
        self.assertEqual(self.client.get("/api/users/").status_code, 403)
        self.assertEqual(self.client.get(f"/api/users/{self.member.pk}/").status_code, 403)

    def test_member_reads_only_self_and_no_secret_fields(self):
        self.login_as(self.member)
        response = self.client.get("/api/users/")
        self.assertEqual([u["id"] for u in response.data["results"]], [self.member.pk])
        own = self.client.get(f"/api/users/{self.member.pk}/")
        self.assertEqual(own.status_code, 200)
        for field in ["password", "is_superuser", "is_staff", "user_permissions", "groups"]:
            self.assertNotIn(field, own.data)
        self.assertEqual(self.client.get(f"/api/users/{self.other.pk}/").status_code, 404)
        self.assertEqual(
            self.client.patch(
                f"/api/users/{self.member.pk}/", {"roles": ["admin"]}, format="json"
            ).status_code,
            403,
        )

    def test_coach_scope_applies_to_list_detail_and_filters(self):
        self.login_as(self.coach)
        users = self.client.get("/api/users/").data["results"]
        self.assertEqual({u["id"] for u in users}, {self.coach.pk, self.member.pk})
        clients = self.client.get("/api/users/?role=member").data["results"]
        self.assertEqual([u["id"] for u in clients], [self.member.pk])
        self.assertEqual(self.client.get(f"/api/users/{self.member.pk}/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/users/{self.other.pk}/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/users/{self.admin.pk}/").status_code, 404)
        self.assertEqual(
            self.client.post(
                f"/api/users/{self.member.pk}/coach/", {"coach_id": self.coach2.pk}
            ).status_code,
            403,
        )

    def test_non_admin_cannot_create_edit_assign_or_read_audit(self):
        for user in [self.member, self.coach]:
            self.login_as(user)
            self.assertEqual(self.client.post("/api/users/", {}, format="json").status_code, 403)
            self.assertEqual(
                self.client.patch(
                    f"/api/users/{self.member.pk}/", {"email": "changed@example.test"}
                ).status_code,
                403,
            )
            self.assertEqual(self.client.get("/api/audit/").status_code, 403)

    def test_admin_creates_roles_and_audits_without_password(self):
        self.login_as(self.admin)
        response = self.client.post(
            "/api/users/",
            {
                "username": "newcoach",
                "email": "new@example.test",
                "password": "UniquePassword!4928",
                "roles": ["coach", "member"],
                "first_name": "Nuevo",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(
            User.objects.get(pk=response.data["id"]).check_password("UniquePassword!4928")
        )
        self.assertEqual(set(response.data["roles"]), {"coach", "member"})
        audit = self.client.get("/api/audit/")
        self.assertEqual(audit.status_code, 200)
        self.assertNotIn("UniquePassword", str(audit.data))
        self.assertNotIn("new@example", str(audit.data))

    def test_assignment_reassignment_and_removal_persist(self):
        self.login_as(self.admin)
        url = f"/api/users/{self.member.pk}/coach/"
        response = self.client.post(url, {"coach_id": self.coach2.pk}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CoachAssignment.objects.get(member=self.member).coach_id, self.coach2.pk)
        self.login_as(self.coach)
        self.assertEqual(self.client.get(f"/api/users/{self.member.pk}/").status_code, 404)
        self.login_as(self.coach2)
        self.assertEqual(self.client.get(f"/api/users/{self.member.pk}/").status_code, 200)
        self.login_as(self.admin)
        self.assertEqual(self.client.post(url, {"coach_id": None}, format="json").status_code, 200)
        self.assertFalse(CoachAssignment.objects.filter(member=self.member).exists())
        self.assertTrue(
            AuditEvent.objects.filter(target=self.member, action="assignment.changed").exists()
        )

    def test_admin_can_also_be_coach(self):
        self.login_as(self.admin)
        response = self.client.patch(
            f"/api/users/{self.admin.pk}/", {"roles": ["admin", "coach"]}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            f"/api/users/{self.member.pk}/coach/", {"coach_id": self.admin.pk}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.has_role("coach"))
        self.assertTrue(
            AuditEvent.objects.filter(target=self.admin, action="roles.changed").exists()
        )

    def test_invalid_assignments_are_rejected(self):
        self.login_as(self.admin)
        for coach_id in [self.member.pk, self.other.pk, 999999]:
            response = self.client.post(
                f"/api/users/{self.member.pk}/coach/", {"coach_id": coach_id}, format="json"
            )
            self.assertEqual(response.status_code, 400)
        response = self.client.post(
            f"/api/users/{self.coach.pk}/coach/", {"coach_id": self.coach2.pk}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_assignment_blocks_role_removal_and_coach_deactivation(self):
        self.login_as(self.admin)
        for target, payload in [
            (self.coach, {"roles": ["member"]}),
            (self.member, {"roles": ["coach"]}),
            (self.coach, {"is_active": False}),
        ]:
            self.assertEqual(
                self.client.patch(f"/api/users/{target.pk}/", payload, format="json").status_code,
                400,
            )

    def test_last_admin_cannot_be_demoted_or_deactivated(self):
        self.login_as(self.admin)
        for payload in [{"roles": ["member"]}, {"is_active": False}]:
            self.assertEqual(
                self.client.patch(
                    f"/api/users/{self.admin.pk}/", payload, format="json"
                ).status_code,
                400,
            )

    def test_readonly_unknown_and_fourth_role_fields_are_rejected(self):
        self.login_as(self.admin)
        for payload in [
            {"is_superuser": True},
            {"is_staff": True},
            {"roles": ["reception"]},
            {"roles": []},
            {"password": "NewPassword!9384"},
        ]:
            self.assertEqual(
                self.client.patch(
                    f"/api/users/{self.member.pk}/", payload, format="json"
                ).status_code,
                400,
            )

    def test_registration_disabled_until_policies_exist(self):
        self.assertEqual(self.client.post("/api/auth/register/", {}).status_code, 403)

    @override_settings(
        REGISTRATION_ENABLED=True,
        TERMS_VERSION="t1",
        PRIVACY_VERSION="p1",
        TERMS_URL="/terms",
        PRIVACY_URL="/privacy",
    )
    def test_public_registration_never_accepts_privileges_and_records_choices(self):
        payload = {
            "username": "publicuser",
            "email": "public@example.test",
            "password": "PublicPassword!3849",
            "terms_version": "t1",
            "privacy_version": "p1",
            "accept_terms": True,
            "accept_privacy": True,
        }
        for field, value in [
            ("roles", ["admin"]),
            ("is_superuser", True),
            ("is_staff", True),
            ("coach_id", self.coach.pk),
        ]:
            response = self.client.post(
                "/api/auth/register/", {**payload, field: value}, format="json"
            )
            self.assertEqual(response.status_code, 400)
        cache.clear()
        response = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["roles"], ["member"])
        self.assertEqual(PolicyAcceptance.objects.filter(user_id=response.data["id"]).count(), 2)

    def test_login_is_rate_limited(self):
        for _ in range(10):
            self.client.post("/api/auth/login/", {"username": "absent", "password": "wrong"})
        self.assertEqual(
            self.client.post(
                "/api/auth/login/", {"username": "absent", "password": "wrong"}
            ).status_code,
            429,
        )

    def test_database_is_mysql(self):
        from django.db import connection

        self.assertEqual(connection.vendor, "mysql")
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            self.assertTrue(cursor.fetchone()[0].startswith("8."))

    def test_bootstrap_administrator_has_business_role_and_audit(self):
        user = User.objects.create_superuser(
            "bootstrap_admin", "bootstrap@example.test", "BootstrapPassword!4392"
        )
        self.assertTrue(user.has_role("admin"))
        self.assertTrue(AuditEvent.objects.filter(target=user, action="user.created").exists())

    def test_private_responses_cannot_be_cached(self):
        self.login_as(self.member)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response["Cache-Control"], "no-store, private")

    def test_admin_coach_panel_filter_shows_only_own_assignments(self):
        self.admin.roles.add(Role.objects.get(slug="coach"))
        self.login_as(self.admin)
        response = self.client.get("/api/users/?role=member&assigned=me")
        self.assertEqual(response.data["results"], [])
        assign_coach(self.admin, self.other.pk, self.admin.pk)
        response = self.client.get("/api/users/?role=member&assigned=me")
        self.assertEqual([u["id"] for u in response.data["results"]], [self.other.pk])
