#!/bin/sh
set -e

# SYSTEM OPTIONS (set on Docker build)
NES_DIR=$NES_DIR

# External database settings
NES_DB_TYPE=${NES_DB_TYPE:-'pgsql'}
NES_DB_HOST=${NES_DB_HOST:-'db'}
NES_DB=${NES_DB:-'nes_db'}
NES_DB_USER=${NES_DB_USER:-'nes_user'}
NES_DB_PORT=${NES_DB_PORT:-'5432'}
NES_DB_PASSWORD=${NES_DB_PASSWORD:-'nes_password'}

# External LimeSurvey settings
LIMESURVEY_HOST=${LIMESURVEY_HOST:-'localhost'}
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

# Entrypoint only variables
NES_PROJECT_PATH="${NES_DIR}/patientregistrationsystem/qdc"
NES_SETUP_PATH="${NES_PROJECT_PATH}/qdc"

if [ "$NES_DB_TYPE" != 'pgsql' ]
then
	echo "Unfortunately, for the time being, NES only works with PostgreSQL."
	exit 1
fi

if [ -f "${NES_SETUP_PATH}"/wsgi.py ]
then
	echo "INFO: NES wsgi.py file already provisioned"
else
	echo "INFO: Creating NES wsgi.py file"
	cat <<-EOF > "${NES_SETUP_PATH}"/wsgi.py
		import os
		import sys
		import site
		paths = ["$NES_PROJECT_PATH", "$NES_DIR", "/usr/local", "/usr/bin", "/bin",]
		for path in paths:
		    if path not in sys.path:
		        sys.path.append(path)
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings")
		from django.core.wsgi import get_wsgi_application
		application = get_wsgi_application()
	EOF
	chown -R nobody "${NES_SETUP_PATH}"/wsgi.py
fi

if [ -f "${NES_SETUP_PATH}"/settings_local.py ]
then
	echo "INFO: NES settings_local.py file already provisioned"
else
	echo "INFO: Creating NES settings_local.py file"
	cat <<-EOF > "${NES_SETUP_PATH}"/settings_local.py
		SECRET_KEY = "$NES_SECRET_KEY"
		DEBUG = True
		DEBUG404 = True
		TEMPLATE_DEBUG = DEBUG
		IS_TESTING = False
		ALLOWED_HOSTS = ["localhost","127.0.0.1","$NES_IP"]
		DATABASES = {
		    "default": {
		        "ENGINE": "django.db.backends.postgresql_psycopg2",
		        "NAME": "$NES_DB",
		        "USER": "$NES_DB_USER",
		        "PASSWORD": "$NES_DB_PASSWORD",
		        "HOST": "$NES_DB_HOST",
		        "PORT": "$NES_DB_PORT", # default port
		    }
		}
		LIMESURVEY = {
		    "URL_API": "http://$LIMESURVEY_HOST:$LIMESURVEY_PORT",
		    "URL_WEB": "http://$LIMESURVEY_HOST:$LIMESURVEY_PORT",
		    "USER": "$LIMESURVEY_ADMIN_USER",
		    "PASSWORD": "$LIMESURVEY_ADMIN_PASSWORD"
		}
		LOGO_INSTITUTION = "logo-institution.png"
	EOF
	chown -R nobody "${NES_SETUP_PATH}"/settings_local.py
fi

while ! nc -z "$NES_DB_HOST" "$NES_DB_PORT"
do
	sleep 0.2
done

if [ -f "${NES_DIR}"/.nes_initialization.placeholder ]
then
	echo "INFO: NES data has already been initialized"
else
	echo "INFO: Initializing NES data (migrations, initial, superuser, ICD)"
	cd "$NES_PROJECT_PATH"

	cat <<-EOF > /tmp/create_superuser.py
		from django.contrib.auth import get_user_model
		User = get_user_model()
		User.objects.create_superuser("$NES_ADMIN_USER", "$NES_ADMIN_EMAIL", "$NES_ADMIN_PASSWORD")
	EOF

	python3 -u manage.py migrate
	# Different versions may have different commands
	python3 -u manage.py shell < add_initial_data.py  || true
	python3 -u manage.py loaddata load_initial_data.json || true
	python3 -u manage.py shell < /tmp/create_superuser.py || true
	python3 -u manage.py import_icd_cid --file icd10cid10v2017.csv || true
	python3 -u manage.py createcachetable || true

	rm /tmp/create_superuser.py

	# If NES was installed from a release it won't have a .git directory
	chown -R nobody "${NES_DIR}"/.git  || true
	chown -R nobody "${NES_DIR}"/patientregistrationsystem

	touch "${NES_DIR}"/.nes_initialization.placeholder
fi

exec "$@"
