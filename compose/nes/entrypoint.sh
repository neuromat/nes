#!/bin/sh
set -ex

# External database settings
NES_DB_TYPE=${NES_DB_TYPE:-'pgsql'}
NES_DB_HOST=${NES_DB_HOST:-'db'}
NES_DB=${NES_DB:-'nes_db'}
NES_DB_USER=${NES_DB_USER:-'nes_user'}
NES_DB_PORT=${NES_DB_PORT:-'5432'}
NES_DB_PASSWORD=${NES_DB_PASSWORD:-'nes_password'}

# External LimeSurvey settings
LIMESURVEY_HOST=${LIMESURVEY_HOST:-'limesurvey'}
LIMESURVEY_PORT=${LIMESURVEY_PORT:-'8080'}
LIMESURVEY_ADMIN_USER=${LIMESURVEY_ADMIN_USER:-'limesurvey_admin'}
LIMESURVEY_ADMIN_PASSWORD=${LIMESURVEY_ADMIN_PASSWORD:-'limesurvey_admin_password'}

# NES specific settings
NES_SECRET_KEY=${NES_SECRET_KEY:-'your_secret_key'}
NES_IP=${NES_IP:-'0.0.0.0'}
NES_PORT=${NES_PORT:-'8000'}
NES_ADMIN_USER=${NES_ADMIN_USER:-'nes_admin'}
NES_ADMIN_EMAIL=${NES_ADMIN_EMAIL:-'nes_admin@nesmail.com'}
NES_ADMIN_PASSWORD=${NES_ADMIN_PASSWORD:-'nes_admin_password'}

if [ "$NES_DB_TYPE" != 'pgsql' ]
then
	echo "Unfortunately, for the time being, NES only works with PostgreSQL."
	exit 1
fi

while ! nc -z "$NES_DB_HOST" "$NES_DB_PORT"
do
	sleep 0.2
done

if [ -f /var/tmp/nes_is_configured ]
then

	echo "NES settings are set"

else

	cat << EOF > /tmp/create_superuser.py
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('$NES_ADMIN_USER', '$NES_ADMIN_EMAIL', '$NES_ADMIN_PASSWORD')
EOF

	cat << EOF > /nes/patientregistrationsystem/qdc/qdc/wsgi.py
import os
import sys
import site
paths = ['/nes/patientregistrationsystem/qdc', '/nes/patientregistrationsystem', '/nes', '/usr/local/bin', '/user/bin', '/bin',]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF

	cat << EOF > /nes/patientregistrationsystem/qdc/qdc/settings_local.py
SECRET_KEY = '$NES_SECRET_KEY'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEBUG404 = True

TEMPLATE_DEBUG = DEBUG

# SECURITY WARNING: don't run with "is testing" on in production
IS_TESTING = False

ALLOWED_HOSTS = ['$NES_IP']

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '$NES_DB',
        'USER': '$NES_DB_USER',
        'PASSWORD': '$NES_DB_PASSWORD',
        'HOST': '$NES_DB_HOST',
        'PORT': '$NES_DB_PORT', # default port
    }
}

# LimeSurvey configuration
LIMESURVEY = {
    'URL_API': 'http://$LIMESURVEY_HOST:$LIMESURVEY_PORT',
    'URL_WEB': 'http://$LIMESURVEY_HOST:$LIMESURVEY_PORT',
    'USER': '$LIMESURVEY_ADMIN_USER',
    'PASSWORD': '$LIMESURVEY_ADMIN_PASSWORD'
}

LOGO_INSTITUTION = 'logo-institution.png'

EOF

	python3 manage.py migrate
	python3 manage.py shell < add_initial_data.py
	python3 manage.py loaddata load_initial_data.json
	python3 manage.py shell < /tmp/create_superuser.py

	touch /var/tmp/nes_is_configured
fi

exec "$@"
