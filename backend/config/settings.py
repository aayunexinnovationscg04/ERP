"""
Django settings for Fuel Guard X backend.

Config comes from backend/.env (see .env.example). Secrets never live in code.
"""

import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env(key, default=None):
    return os.environ.get(key, default)


def env_bool(key, default=False):
    return str(env(key, str(default))).lower() in ("1", "true", "yes", "on")


def env_list(key, default=""):
    return [x.strip() for x in env(key, default).split(",") if x.strip()]


# --- core ---------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "corsheaders",
    # local
    "core",
    "fleet",
    "ingest",
    "alerts",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
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
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# --- database (parsed from DATABASE_URL) --------------------------------
def _db_from_url(url):
    p = urlparse(url)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": p.path.lstrip("/"),
        "USER": p.username or "",
        "PASSWORD": p.password or "",
        "HOST": p.hostname or "127.0.0.1",
        "PORT": str(p.port or 5432),
        "CONN_MAX_AGE": 60,  # persistent connections — cheap win for the API
    }


DATABASES = {
    "default": _db_from_url(
        env("DATABASE_URL", "postgres://fuelguardx@127.0.0.1:5432/fuelguardx")
    )
}

AUTH_USER_MODEL = "core.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
# Served by nginx (unprivileged www-data), so it must live outside /root (mode 700).
STATIC_ROOT = Path("/var/www/fuelguardx/static")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- DRF + JWT ----------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 50,
    # Brute-force / abuse throttling. Anonymous hits (login, ingest) are the hot
    # target, so they get the tightest bucket via the 'login' scope on the view.
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "2000/hour",
        "login": "10/min",
    },
}

SIMPLE_JWT = {
    # Short-lived access token; the SPAs silently refresh on 401. Refresh is 7 days.
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- CORS ---------------------------------------------------------------
# In production the SPAs are served same-origin (erp.aayunexinnovations.com), so
# CORS is not needed there. This allowlist only exists for local Vite dev servers.
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:5175",
)
CORS_ALLOW_CREDENTIALS = False  # we use bearer tokens, never cookies, cross-origin

# --- device ingest ------------------------------------------------------
INGEST_TOKEN = env("INGEST_TOKEN", "fuelguardx")


# --- production security -------------------------------------------------
# Django runs behind Caddy (TLS) -> nginx -> gunicorn (plain HTTP on loopback).
# Trust the proxy's X-Forwarded-Proto so request.is_secure() is correct, then
# turn on the cookie/redirect/HSTS protections that depend on it.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS", "https://erp.aayunexinnovations.com"
)
X_FRAME_OPTIONS = "DENY"                     # no framing of Django admin
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

if not DEBUG:
    SESSION_COOKIE_SECURE = True             # admin session cookie: HTTPS only
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    # HSTS is also set at the Caddy edge; setting it here is belt-and-suspenders
    # for any response Django emits directly.
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False    # only erp/dashboard are on this apex
    SECURE_HSTS_PRELOAD = False

# Derivation defaults (per-company overrides live in core.CompanySettings)
DERIVATION_DEFAULTS = {
    "overspeed_limit_kmph": 60,
    "offline_after_seconds": 900,
    "theft_drop_litres": 5,
}
