import json
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")
APP_CONFIG = json.loads((BASE_DIR.parent / "config" / "app.json").read_text(encoding="utf-8"))
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    raise ImproperlyConfigured("Configure DJANGO_SECRET_KEY en backend/.env.")
DEBUG = False
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS", "http://127.0.0.1:9000,http://localhost:9000"
).split(",")
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.users",
    "apps.audit",
    "apps.privacy",
]
MIDDLEWARE = [
    "common.middleware.PrivateApiMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
AUTH_USER_MODEL = "users.User"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DATABASE", "gym_development"),
        "USER": os.getenv("MYSQL_USER", "gym_app"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", ""),
        "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "PORT": os.getenv("MYSQL_PORT", "3307"),
        "OPTIONS": {"charset": "utf8mb4", "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
        "TEST": {"NAME": os.getenv("MYSQL_TEST_DATABASE", "gym_test")},
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "es-cr"
TIME_ZONE = APP_CONFIG["timezone"]
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 8
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
REST_FRAMEWORK = {
    "NUM_PROXIES": 0,
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "EXCEPTION_HANDLER": "common.exceptions.api_exception_handler",
    "DEFAULT_THROTTLE_RATES": {"login": "10/min", "registration": "5/hour"},
}
REGISTRATION_ENABLED = os.getenv("REGISTRATION_ENABLED", "false").lower() == "true"
TERMS_VERSION = os.getenv("TERMS_VERSION", "")
PRIVACY_VERSION = os.getenv("PRIVACY_VERSION", "")
TERMS_URL = os.getenv("TERMS_URL", "")
PRIVACY_URL = os.getenv("PRIVACY_URL", "")
