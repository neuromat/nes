SECRET_KEY = 'f#&1%$3(#1&9rb6dk7i@%vzr^wh8*&4x8m3*!g#v*w7ffa23kn'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
    'django_jenkins.tasks.run_sloccount',
    'django_jenkins.tasks.run_pylint',
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': 'database_name',
        'USER': 'db_user_name',
        'PASSWORD': 'db_user_pwd',
        'HOST': 'host_name_or_ip',
    }
}

# LimeSurvey configuration
LIMESURVEY = {
    'URL_API': 'http://example.limesurvey.server.com',
    'URL_WEB': 'http://example.limesurvey.server.com',
    'USER': 'limesurvey_user_name',
    'PASSWORD': 'limesurvey_user_pwd'
}

# Settings to send emails
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'smtp.user@example.com'
EMAIL_HOST_PASSWORD = 'smtp.user_pwd'
DEFAULT_FROM_EMAIL = 'smtp.user@example.com'
SERVER_EMAIL = EMAIL_HOST_USER

# version
VERSION = '0.3.1'

CONTACT_INSTITUTION = 'Developer environment'
CONTACT_EMAIL = 'contact at example dot com'
CONTACT_URL = 'https://example.com'
