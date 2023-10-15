from .base import *

DEBUG = False
DEBUG404 = False
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

CACHE_MIDDLEWARE_ALIAS = "default"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}

DJANGO_LOG_LEVEL = "CRITICAL"
