#!/bin/sh
set -e

PGDATA=${PGDATA:-"/var/lib/postgresql/data"}

# LIMESURVEY
## SYSTEM OPTIONS
LIMESURVEY_HOST=${LIMESURVEY_HOST:-"limesurvey"}
LIMESURVEY_PORT=${LIMESURVEY_PORT:-"8080"}
LIMESURVEY_DIR="$LIMESURVEY_DIR"
APACHE2_CONF_DIR="$LIMESURVEY_DIR/application/config"
## CONFIG.PHP OPTIONS
LIMESURVEY_DB_HOST=${LIMESURVEY_DB_HOST:-"127.0.0.1"}
LIMESURVEY_DB_PORT=${LIMESURVEY_DB_PORT:-"5432"}
LIMESURVEY_DB_NAME=${LIMESURVEY_DB_NAME:-"limesurvey_db"}
LIMESURVEY_DB_TABLE_PREFIX=${LIMESURVEY_DB_TABLE_PREFIX:-"lime_"}
LIMESURVEY_DB_USER=${LIMESURVEY_DB_USER:-"limesurvey_user"}
LIMESURVEY_DB_PASSWORD=${LIMESURVEY_DB_PASSWORD:-"limesurvey_password"}
LIMESURVEY_DB_CHARSET=${LIMESURVEY_DB_CHARSET:-"utf8"}
LIMESURVEY_URL_FORMAT=${LIMESURVEY_URL_FORMAT:-"path"}
## SUPER USER CREATION OPTION
LIMESURVEY_ADMIN_USER=${LIMESURVEY_ADMIN_USER:-"lime_admin"}
LIMESURVEY_ADMIN_NAME=${LIMESURVEY_ADMIN_NAME:-"lime_admin_name"}
LIMESURVEY_ADMIN_EMAIL=${LIMESURVEY_ADMIN_EMAIL:-"limesurvey@limemail.false"}
LIMESURVEY_ADMIN_PASSWORD=${LIMESURVEY_ADMIN_PASSWORD:-"lime_admin_password"}
# NES
## SYSTEM OPTIONS
#NES_DIR=${NES_DIR:-"/usr/local/nes"}
## SETTINGS_LOCAL OPTIONS
### DJANGO
NES_SECRET_KEY=${NES_SECRET_KEY:-"your_secret_key"}
NES_IP=${NES_IP:-"0.0.0.0"}
NES_PORT=${NES_PORT:-"80"}
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
#NES_SETUP_PATH=${NES_SETUP_PATH:-"/usr/local/nes/setup"}

# SUPERVISOR
#SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/etc/supervisor"}

# Entrypoint only variable
NES_PROJECT_PATH="$NES_DIR/patientregistrationsystem/qdc"

if [ $NES_DB_TYPE != "pgsql" ]; then
    echo "Unfortunately, for the time being, NES only works with PostgreSQL."
    exit 1
fi

mkdir -p $NES_PROJECT_PATH

# NES SETUP ####################################################
if [ -f $NES_PROJECT_PATH/nes_wsgi.placeholder ]; then
    echo "INFO: NES wsgi.py file already provisioned"
else
    echo "INFO: Creating NES wsgi.py file"
	cat <<-EOF >$NES_PROJECT_PATH/qdc/wsgi.py
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
    chown -R nobody $NES_PROJECT_PATH/qdc/wsgi.py
    touch $NES_PROJECT_PATH/nes_wsgi.placeholder
	chown -R nobody $NES_PROJECT_PATH/nes_wsgi.placeholder
fi

if [ -f $NES_PROJECT_PATH/nes_settings.placeholder ]; then
    echo "INFO: NES settings_local.py file already provisioned"
else
    echo "INFO: Creating NES settings_local.py file"
	cat <<-EOF >$NES_PROJECT_PATH/qdc/settings_local.py
		SECRET_KEY = "$NES_SECRET_KEY"
		DEBUG = True
		DEBUG404 = True
		TEMPLATE_DEBUG = DEBUG
		IS_TESTING = True
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
		LOGO_INSTITUTION = "$NES_PROJECT_PATH/logo-institution.png"
	EOF
    chown -R nobody $NES_PROJECT_PATH/qdc/settings_local.py
    touch $NES_PROJECT_PATH/nes_settings.placeholder
	chown -R nobody $NES_PROJECT_PATH/nes_settings.placeholder
fi
echo "criou arquivos de config"
while ! nc -z "$NES_DB_HOST" "$NES_DB_PORT"; do
    sleep 0.2
done

# INITIALIZE DATA ####################################################

## NES
if [ -f $NES_DIR/.nes_initialization.placeholder ]; then
    echo "INFO: NES data has already been initialized"
else
    echo "INFO: Initializing NES data (migrations, initial, superuser, ICD)"
    cd $NES_DIR/patientregistrationsystem/qdc/
    
	cat <<-EOF >/tmp/create_superuser.py
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    User.objects.create_superuser("$NES_ADMIN_USER", "$NES_ADMIN_EMAIL", "$NES_ADMIN_PASSWORD")
    User.objects.create_superuser("carjulio", "carjulio@peb.ufrj.br", "carlosjulio2023")
except:
    print("erro criando super usuario.")
	EOF
    
	echo "	INFO: makemigrations"
	python3 -u manage.py makemigrations || true
    echo "	INFO: Migrate"
    python3 -u manage.py migrate || true
    # Different versions may have different commands
    echo "	INFO: add_initial_data.py"
    python3 -u manage.py shell < add_initial_data.py || true
    echo "	INFO: load_initial_data.py"
    python3 -u manage.py loaddata load_initial_data.json || true
    echo "INFO create cachetable"
    python3 -u manage.py createcachetable || true
    echo "	INFO: create_super_ser.py"
    python3 -u manage.py shell < /tmp/create_superuser.py || true
    echo "	INFO: import cid10"
    python -u manage.py import_icd_cid --file icd10cid10v2017.csv || true

	mkdir static || true
	echo "INFO: colectstatic"
	python3 -u manage.py collectstatic --no-input || true

    
    rm /tmp/create_superuser.py
    
    # If NES was installed from a release it won"t have a .git directory
    #chown -R nobody $NES_DIR/.git || true
    chown -R vscode $NES_DIR/patientregistrationsystem
    
    touch $NES_DIR/.nes_initialization.placeholder
	chown -R nobody $NES_DIR/.nes_initialization.placeholder
fi

echo "Done"

echo "entrypoint.sh finished"

exec "$@"
