#!/bin/sh
set -e

PGDATA=${PGDATA:-"/var/lib/postgresql/data"}

# LIMESURVEY
## SYSTEM OPTIONS
LIMESURVEY_HOST=${LIMESURVEY_HOST:-"localhost"}
LIMESURVEY_PORT=${LIMESURVEY_PORT:-"8080"}
LIMESURVEY_DIR="$LIMESURVEY_DIR"
APACHE2_CONF_DIR="$LIMESURVEY_DIR/application/config"
## CONFIG.PHP OPTIONS
LIMESURVEY_DB_HOST=${LIMESURVEY_DB_HOST:-"localhost"}
LIMESURVEY_DB_PORT=${LIMESURVEY_DB_PORT:-"5433"}
LIMESURVEY_DB_NAME=${LIMESURVEY_DB_NAME:-"limesurvey_db"}
LIMESURVEY_DB_TABLE_PREFIX=${LIMESURVEY_DB_TABLE_PREFIX:-"lime_"}
LIMESURVEY_DB_USER=${LIMESURVEY_DB_USER:-"limesurvey_user"}
LIMESURVEY_DB_PASSWORD=${LIMESURVEY_DB_PASSWORD:-"limesurvey_password"}
LIMESURVEY_DB_CHARSET=${LIMESURVEY_DB_CHARSET:-"utf8"}
LIMESURVEY_URL_FORMAT=${LIMESURVEY_URL_FORMAT:-"path"}
## SUPER USER CREATION OPTION
LIMESURVEY_ADMIN_USER=${LIMESURVEY_ADMIN_USER:-"limesurvey_admin"}
LIMESURVEY_ADMIN_NAME=${LIMESURVEY_ADMIN_NAME:-"limesurvey_admin_name"}
LIMESURVEY_ADMIN_EMAIL=${LIMESURVEY_ADMIN_EMAIL:-"limesurvey@limemail.false"}
LIMESURVEY_ADMIN_PASSWORD=${LIMESURVEY_ADMIN_PASSWORD:-"limesurvey_admin_password"}
# NES
## SYSTEM OPTIONS
NES_DIR=${NES_DIR:-"/usr/local/nes"}
## SETTINGS_LOCAL OPTIONS
### DJANGO
NES_SECRET_KEY=${NES_SECRET_KEY:-"your_secret_key"}
NES_IP=${NES_IP:-0.0.0.0}
NES_PORT=${NES_PORT:-8000}
NES_ADMIN_USER=${NES_ADMIN_USER:-"nes_admin"}
NES_ADMIN_EMAIL=${NES_ADMIN_EMAIL:-"nes_admin@nesmail.false"}
NES_ADMIN_PASSWORD=${NES_ADMIN_PASSWORD:-"nes_admin_password"}
### DB
#### External database settings
NES_DB_TYPE=${NES_DB_TYPE:-"pgsql"}
NES_DB_HOST=${NES_DB_HOST:-"nes_db"}
NES_DB_PORT=${NES_DB_PORT:-"5432"}
NES_DB=${NES_DB:-"nes_db"}
NES_DB_USER=${NES_DB_USER:-"nes_user"}
NES_DB_PASSWORD=${NES_DB_PASSWORD:-"nes_password"}
NES_SETUP_PATH=${NES_SETUP_PATH:-"/usr/local/nes"}

# SUPERVISOR
#SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/etc/supervisor"}

# Entrypoint only variable
NES_PROJECT_PATH="$NES_DIR/patientregistrationsystem/qdc"

if [ "$NES_DB_TYPE" != "pgsql" ]; then
    echo "Unfortunately, for the time being, NES only works with PostgreSQL."
    exit 1
fi

mkdir -p $NES_SETUP_PATH

# NES SETUP ####################################################
if [ -f $NES_SETUP_PATH/nes_wsgi.placeholder ]; then
    echo "INFO: NES wsgi.py file already provisioned"
else
    echo "INFO: Creating NES wsgi.py file"
	sudo cat <<-EOF >"$NES_PROJECT_PATH"/qdc/wsgi.py
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
    sudo chown -R nobody "$NES_PROJECT_PATH"/qdc/wsgi.py
    touch "$NES_SETUP_PATH"/nes_wsgi.placeholder
fi

if [ -f "$NES_SETUP_PATH"/nes_settings.placeholder ]; then
    echo "INFO: NES settings_local.py file already provisioned"
else
    echo "INFO: Creating NES settings_local.py file"
	sudo cat <<-EOF >"$NES_PROJECT_PATH"/qdc/settings_local.py
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
    sudo chown -R nobody "$NES_PROJECT_PATH"/qdc/settings_local.py
    touch "$NES_SETUP_PATH"/nes_settings.placeholder
fi

while ! nc -z "$NES_DB_HOST" "$NES_DB_PORT"; do
    sleep 0.2
done

# Enables django runserver to write its logs to stdout
sudo chmod a+w /dev/pts/0

echo "entrypoint.sh finished"

/bin/sh $NES_DIR/scripts/init_data.sh

exec "$@"
