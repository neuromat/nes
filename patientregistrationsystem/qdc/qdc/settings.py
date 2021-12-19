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

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
DEBUG404 = False

# Put this line in local settings to put in maintenance mode, or uncomment, and
# restart application server
# MAINTENANCE_MODE = True

# SECURITY WARNING: don't run with "is testing" in production
IS_TESTING = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600

# Application definition

INSTALLED_APPS = (
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_jenkins",
    "simple_history",
    "jsonrpc_requests",
    "solo",
    "fixture_magic",
    "maintenance_mode",
)

PROJECT_APPS = (
    "quiz",
    "patient",
    "custom_user",
    "experiment",
    "survey",
    "export",
    "configuration",
    "plugin",
)

INSTALLED_APPS += PROJECT_APPS

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "qdc.middleware.PasswordChangeMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "maintenance_mode.middleware.MaintenanceModeMiddleware",
)

CONTEXT_PROCESSORS = {"maintenance_mode.context_processors.maintenance_mode"}

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

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "limesurveycache",
        "TIMEOUT": 24 * 60 * 60,
    }
}

ROOT_URLCONF = "qdc.urls"

WSGI_APPLICATION = "qdc.wsgi.application"

# LimeSurvey configuration
LIMESURVEY = {
    "URL_API": "",
    "URL_WEB": "",
    "USER": "",
    "PASSWORD": "",
}

# Portal API configuration
PORTAL_API = {"URL": "", "PORT": "", "USER": "", "PASSWORD": ""}

# Show button to send experiments to Portal
SHOW_SEND_TO_PORTAL_BUTTON = False

# AUTH_USER_MODEL = 'quiz.UserProfile'
# AUTH_PROFILE_MODULE = 'quiz.UserProfile'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = "es"

LANGUAGES = (
    ("pt-br", "Português"),
    ("en", "English"),
    ("es", "Español"),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
    os.path.join(BASE_DIR, "patient/locale"),
    os.path.join(BASE_DIR, "experiment/locale"),
    os.path.join(BASE_DIR, "survey/locale"),
    os.path.join(BASE_DIR, "custom_user/locale"),
    os.path.join(BASE_DIR, "quiz/locale"),
    os.path.join(BASE_DIR, "export/locale"),
    os.path.join(BASE_DIR, "qdc/locale"),
)

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Database Translation
MODELTRANSLATION_LANGUAGES = ("pt-br", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("pt-br", "en")

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

STATIC_ROOT = ""
STATIC_URL = "/static/"

ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

try:
    from .settings_local import *
except ImportError:
    pass

VERSION = "1.72.7"
