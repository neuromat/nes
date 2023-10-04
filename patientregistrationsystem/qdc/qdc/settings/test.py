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


DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3"}

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
