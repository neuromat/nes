from .base import *

DEBUG = False
DEBUG404 = False
TEMPLATE_DEBUG = DEBUG
IS_TESTING = True

AXES_ENABLED = False

SECURE_SSL_REDIRECT = False
CSRF_USE_SESSIONS = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": "test_database",
}

PASSWORD_HASHERS: list[str] = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

DJANGO_LOG_LEVEL = "CRITICAL"
