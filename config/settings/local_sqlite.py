"""Loopback-only development settings for learners without a local PostgreSQL service."""
import os
import secrets

from django.core.exceptions import ImproperlyConfigured
from .base import *

if os.getenv("VERCEL"):
    raise ImproperlyConfigured("Use config.settings.production for deployment; local SQLite is not deployable.")

DEBUG = True
TRAINING_MODE = False
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or secrets.token_urlsafe(50)
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "incidentdesk-dev.sqlite3",
    }
}
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
