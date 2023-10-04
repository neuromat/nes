SECRET_KEY = "your_secret_key"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
DEBUG404 = True

TEMPLATE_DEBUG = DEBUG

# SECURITY WARNING: don't run with "is testing" on in production
IS_TESTING = False

ALLOWED_HOSTS: list[str] = ["*"]

# https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-STATIC_ROOT
STATIC_ROOT = ""

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "database_name",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432",  # default port
    }
}

# LimeSurvey configuration
LIMESURVEY = {
    "URL_API": "http://example.limesurvey.server.com",
    "URL_WEB": "http://example.limesurvey.server.com",
    "USER": "limesurvey_user",
    "PASSWORD": "limesurvey_password",
}

# Settings to send emails
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.example.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "smtp.user@example.com"
EMAIL_HOST_PASSWORD = "smtp.user_pwd"
DEFAULT_FROM_EMAIL = "smtp.user@example.com"
SERVER_EMAIL = EMAIL_HOST_USER

CONTACT_INSTITUTION = "Developer environment"
CONTACT_EMAIL = "contact at example dot com"
CONTACT_URL = "https://example.com"
LOGO_INSTITUTION = "logo-institution.png"
