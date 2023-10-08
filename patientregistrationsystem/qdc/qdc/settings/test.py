from .base import *

DEBUG = True
DEBUG404 = True
TEMPLATE_DEBUG = DEBUG
IS_TESTING = True

AXES_ENABLED = False

SECURE_SSL_REDIRECT = False
CSRF_USE_SESSIONS = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3"}

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
