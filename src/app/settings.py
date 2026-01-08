from __future__ import annotations

import os
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).resolve().parent.parent


def env_str(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if val is None or str(val).strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return str(val)


def env_bool(name: str, default: str = "0") -> bool:
    return str(os.getenv(name, default)).strip().lower() in {"1", "true", "yes", "on"}


def env_csv(name: str, default: str = "") -> List[str]:
    raw = str(os.getenv(name, default)).strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


SECRET_KEY = env_str("DJANGO_SECRET_KEY")
DEBUG = env_bool("DJANGO_DEBUG", "0")

ALLOWED_HOSTS = env_csv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

CSRF_TRUSTED_ORIGINS = env_csv("DJANGO_CSRF_TRUSTED_ORIGINS", "")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

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
    }
]

WSGI_APPLICATION = "app.wsgi.application"
ASGI_APPLICATION = "app.asgi.application"

DATABASE_URL = env_str("DATABASE_URL")

if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://"):
    ENGINE = "django.db.backends.postgresql"
else:
    ENGINE = "django.db.backends.sqlite3"

if ENGINE == "django.db.backends.postgresql":
    from urllib.parse import urlparse

    u = urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": ENGINE,
            "NAME": (u.path or "").lstrip("/"),
            "USER": u.username,
            "PASSWORD": u.password,
            "HOST": u.hostname,
            "PORT": u.port or 5432,
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STRIPE_SUCCESS_URL = env_str("STRIPE_SUCCESS_URL")
STRIPE_CANCEL_URL = env_str("STRIPE_CANCEL_URL")

STRIPE_CURRENCY_DEFAULT = os.getenv("STRIPE_CURRENCY_DEFAULT", "usd").strip().lower()

STRIPE_USD_SECRET_KEY = env_str("STRIPE_USD_SECRET_KEY")
STRIPE_USD_PUBLISHABLE_KEY = env_str("STRIPE_USD_PUBLISHABLE_KEY")

STRIPE_EUR_SECRET_KEY = env_str("STRIPE_EUR_SECRET_KEY")
STRIPE_EUR_PUBLISHABLE_KEY = env_str("STRIPE_EUR_PUBLISHABLE_KEY")

STRIPE_PAYMENT_MODE = os.getenv("STRIPE_PAYMENT_MODE", "checkout_session").strip().lower()
if STRIPE_PAYMENT_MODE not in {"checkout_session", "payment_intent"}:
    raise RuntimeError("STRIPE_PAYMENT_MODE must be 'checkout_session' or 'payment_intent'")
