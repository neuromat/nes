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
SECRET_KEY = 'f#&1%$3(#1&9rb6dk7i@%vzr^wh8*&4x8m3*!g#v*w7ffa23kn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

PROJECT_APPS = ['quiz', 'experiment']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'quiz',
    'experiment',
    'django_jenkins',
    'simple_history',
    'cep',
)

JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
    # 'django_jenkins.tasks.django_tests',   # select one django or
    # 'django_jenkins.tasks.dir_tests'      # directory tests discovery
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
    # 'django_jenkins.tasks.run_jslint',
    # 'django_jenkins.tasks.run_csslint',
    'django_jenkins.tasks.run_sloccount',
    # 'django_jenkins.tasks.lettuce_tests',
    'django_jenkins.tasks.run_pylint',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'qdc.urls'

WSGI_APPLICATION = 'qdc.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'qdcdb_dev',
        'USER': 'qdc',
        'PASSWORD': 'DEVqdc1716',
        # 'HOST': '200.144.254.136',
        # 'TEST_NAME': 'test_romulo',
    }
}

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'pt-br'

LANGUAGES = (
    ('pt-br', u'Português'),
    ('en', u'English'),
)

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Settings to send emails
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'jenkins.neuromat@gmail.com'
EMAIL_HOST_PASSWORD = 'numecusp'
DEFAULT_FROM_EMAIL = 'jenkins.neuromat@gmail.com'
SERVER_EMAIL = EMAIL_HOST_USER

# if DEBUG:
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_HOST_USER = ''
#     EMAIL_HOST_PASSWORD = ''
#     EMAIL_USE_TLS = False
#     DEFAULT_FROM_EMAIL = 'testing@example.com'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = '/home/crns/PycharmProjects/neuromat-cc-ribas/patientregistrationsystem/qdc/quiz/'
# STATIC_ROOT = [os.path.join(BASE_DIR, 'static')]
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
