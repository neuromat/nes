# -*- coding: utf-8 -*-
"""
Django settings for qdc project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from pathlib import Path
from django.utils.translation import gettext_lazy as _


BASE_DIR: Path = Path(__file__).parent.parent.parent

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = ""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEBUG404 = True

# Put this line in local settings to put in maintenance mode, or uncomment, and
# restart application server
# MAINTENANCE_MODE = True

# SECURITY WARNING: don't run with "is testing" in production
IS_TESTING = True


AXES_COOLOFF_MESSAGE = _(
    "Your accouunt has been locked for 1 hour: too many login attempts."
)
AXES_FAILURE_LIMIT = 5
AXES_RESET_ON_SUCCESS = True
AXES_COOLOFF_TIME = 1

ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "0.0.0.0"]


SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600

CONN_MAX_AGE = 3600
CONN_HEALTH_CHECKS = True


# Application definition

INSTALLED_APPS: list[str] = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "simple_history",
    "jsonrpclib",
    "solo",
    "fixture_magic",
    "maintenance_mode",
    "rosetta",
    "axes",
]

PROJECT_APPS: list[str] = [
    "patient",
    "custom_user",
    "experiment",
    "survey",
    "export",
    "configuration",
    "plugin",
    "processing",
]

INSTALLED_APPS += PROJECT_APPS

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    # "django.middleware.cache.UpdateCacheMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "django.middleware.cache.FetchFromCacheMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "maintenance_mode.middleware.MaintenanceModeMiddleware",
    "axes.middleware.AxesMiddleware",
    "qdc.middleware.PasswordChangeMiddleware",
]

CONTEXT_PROCESSORS = {
    "maintenance_mode.context_processors.maintenance_mode",
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
            "debug": DEBUG,
        },
    },
]

AUTHENTICATION_BACKENDS: list[str] = [
    # AxesStandaloneBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    "axes.backends.AxesStandaloneBackend",
    # Django ModelBackend is the default authentication backend.
    "django.contrib.auth.backends.ModelBackend",
]

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

CACHE_MIDDLEWARE_ALIAS = "redis"
CACHE_MIDDLEWARE_KEY_PREFIX = ""
CACHE_MIDDLEWARE_SECONDS = 60 * 60

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "limesurveycache",
        "TIMEOUT": 24 * 60 * 60,
    },
    "redis": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    },
}

ROOT_URLCONF = "qdc.urls"

WSGI_APPLICATION = "qdc.wsgi.application"

# LimeSurvey configuration
LIMESURVEY: dict[str, str] = {
    "URL_API": "",
    "URL_WEB": "",
    "USER": "",
    "PASSWORD": "",
}

# Portal API configuration
PORTAL_API: dict[str, str] = {"URL": "", "PORT": "", "USER": "", "PASSWORD": ""}

# Show button to send experiments to Portal
SHOW_SEND_TO_PORTAL_BUTTON = False

# AUTH_USER_MODEL = 'quiz.UserProfile'
# AUTH_PROFILE_MODULE = 'quiz.UserProfile'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = "pt-br"

LANGUAGES = (
    (
        "pt-br",
        _("Português"),
    ),
    (
        "en",
        _("English"),
    ),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
    os.path.join(BASE_DIR, "patient/locale"),
    os.path.join(BASE_DIR, "experiment/locale"),
    os.path.join(BASE_DIR, "survey/locale"),
    os.path.join(BASE_DIR, "custom_user/locale"),
    os.path.join(BASE_DIR, "export/locale"),
    os.path.join(BASE_DIR, "processing/locale"),
    os.path.join(BASE_DIR, "qdc/locale"),
    os.path.join(BASE_DIR, "site_static/locale"),
)

USE_TZ = True
TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_L10N = True

# Database Translation
MODELTRANSLATION_LANGUAGES = (
    "pt-br",
    "en",
)
MODELTRANSLATION_FALLBACK_LANGUAGES = (
    "pt-br",
    "en",
)

MODELTRANSLATION_TRANSLATION_FILES = (
    "patient.translation",
    "experiment.translation",
    # '<APP2_MODULE>.translation',
)

MODELTRANSLATION_CUSTOM_FIELDS = (
    "name",
    "description",
    "abbreviated_description",
)

MODELTRANSLATION_AUTO_POPULATE = "all"

MODELTRANSLATION_PREPOPULATE_LANGUAGE = "en"

FIXTURE_DIRS = (
    "patient.fixtures",
    "experiment.fixtures",
)

# The maximum number of parameters that may be received via GET or POST
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS: list[str] = [
    os.path.join(BASE_DIR, "site_static"),
]

STATIC_ROOT: str = os.path.join(BASE_DIR, "static")
STATIC_URL = "static/"

ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

MEDIA_ROOT: str = os.path.join(BASE_DIR, "media")
MEDIA_URL = "media/"

try:
    from .settings_local import *
except ImportError:
    pass

VERSION = "2.0.0"
