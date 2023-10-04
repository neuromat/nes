from .base import *

DEBUG = True
DEBUG404 = True
TEMPLATE_DEBUG = DEBUG
IS_TESTING = True

AXES_ENABLED = True


# SECURE_SSL_REDIRECT = True
CSRF_USE_SESSIONS = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True


INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEBUG_TOOLBAR_CONFIG = {
    "JQUERY_URL": "",
}
