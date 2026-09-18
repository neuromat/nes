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
# Fase1: via env (compose já passa NES_SECRET_KEY). Mantém compatível com Django 2.2.
SECRET_KEY = os.environ.get('NES_SECRET_KEY', '') or 'unsafe-dev-only'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
DEBUG404 = False

# Put this line in local settings to put in maintenance mode, or uncomment, and
# restart application server
#MAINTENANCE_MODE = True

# SECURITY WARNING: don't run with "is testing" in production
IS_TESTING = True

# Fase1: hosts via env NES_ALLOWED_HOSTS (vírgula), + defaults locais. Compatível Django 2.2.
ALLOWED_HOSTS = [h.strip() for h in os.environ.get(
    'NES_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600

# Application definition

INSTALLED_APPS = (
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Fase2: django_jenkins removido (morto, bloqueia Django 4.x). Ver requirements.txt.
    'simple_history',
    'jsonrpc_requests',
    'solo',
    'fixture_magic',
    'maintenance_mode'
)

PROJECT_APPS = (
    'quiz',
    'patient',
    'custom_user',
    'experiment',
    'survey',
    'export',
    'configuration',
    'plugin'
)

INSTALLED_APPS += PROJECT_APPS

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'qdc.middleware.PasswordChangeMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
]

CONTEXT_PROCESSORS = {
    'maintenance_mode.context_processors.maintenance_mode'
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            'debug': DEBUG,
        },
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'limesurveycache',
        'TIMEOUT': 24*60*60,

    }
}

ROOT_URLCONF = 'qdc.urls'

WSGI_APPLICATION = 'qdc.wsgi.application'

# LimeSurvey configuration
LIMESURVEY = {
    'URL_API': '',
    'URL_WEB': '',
    'USER': '',
    'PASSWORD': '',
}

# Portal API configuration
PORTAL_API = {
    'URL': '',
    'PORT': '',
    'USER': '',
    'PASSWORD': ''
}

# Show button to send experiments to Portal
SHOW_SEND_TO_PORTAL_BUTTON = False

# AUTH_USER_MODEL = 'quiz.UserProfile'
# AUTH_PROFILE_MODULE = 'quiz.UserProfile'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'pt-br'

LANGUAGES = (
    ('pt-br', 'Português'),
    ('en', 'English'),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR, 'patient/locale'),
    os.path.join(BASE_DIR, 'experiment/locale'),
    os.path.join(BASE_DIR, 'survey/locale'),
    os.path.join(BASE_DIR, 'custom_user/locale'),
    os.path.join(BASE_DIR, 'quiz/locale'),
    os.path.join(BASE_DIR, 'export/locale'),
    os.path.join(BASE_DIR, 'qdc/locale'),
)

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

# Fase3b: USE_L10N removido (deprecated 4.0, removido 5.0). No 4.x formatação local é o padrão.

USE_TZ = True

# Database Translation
MODELTRANSLATION_LANGUAGES = ('pt-br', 'en')
MODELTRANSLATION_FALLBACK_LANGUAGES = ('pt-br', 'en')

MODELTRANSLATION_TRANSLATION_FILES = (
    'patient.translation',
    'experiment.translation',
    # '<APP2_MODULE>.translation',
)

MODELTRANSLATION_CUSTOM_FIELDS = ('name', 'description', 'abbreviated_description', )

MODELTRANSLATION_AUTO_POPULATE = 'all'

MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en'

FIXTURE_DIRS = (
    'patient.fixtures',
    'experiment.fixtures',
)

# The maximum number of parameters that may be received via GET or POST
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Fase3a: evita migração implícita p/ BigAutoField no Django 3.2+. Revisar na 5.2.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# Fase1: STATIC_ROOT via env, default coletável. Compatível Django 2.2.
STATIC_ROOT = os.environ.get('NES_STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))
STATIC_URL = '/static/'

# Fase5: storage com hash p/ cache busting (estilo STORAGES do 4.2+; STATICFILES_STORAGE removido no 5.1).
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'qdc.storage.LegacyManifestStaticFilesStorage'},
}

# Fase5: baseline de headers. CSP enforce fica p/ depois (muito JS inline legado) —
# quando for a hora, usar django-csp em modo report-only primeiro.
SECURE_CONTENT_TYPE_NOSNIFF = True

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

try:
    from .settings_local import *
except ImportError:
    pass

VERSION = '1.73.0'
