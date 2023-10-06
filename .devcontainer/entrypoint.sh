#!/bin/sh
set -e

# Entrypoint only variable
NES_PROJECT_PATH="$NES_DIR/patientregistrationsystem/qdc"


echo "INFO: Starting entrypoint.sh"

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
		paths = ["$NES_PROJECT_PATH", "$NES_DIR", "/usr/local", "/usr/bin", "/bin", "/usr/local/nes", ]
		for path in paths:
		    if path not in sys.path:
		        sys.path.append(path)
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings.dev")
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
	cat <<-EOF >$NES_PROJECT_PATH/qdc/settings/settings_local.py
		SECRET_KEY = "$NES_SECRET_KEY"
		ALLOWED_HOSTS = ["localhost", "127.0.0.1", "$NES_IP", "$NES_HOSTNAME"]
CSRF_TRUSTED_ORIGINS = ["https://localhost:80", "https://$NES_IP", "https://$NES_HOSTNAME", ]
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
    chown -R nobody $NES_PROJECT_PATH/qdc/settings/settings_local.py
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
    python3 -u manage.py loaddata load_eeg_initial_data.json || true
    echo "	INFO create cachetable"
    python3 -u manage.py createcachetable || true
    echo "	INFO: create_super_user.py"
    python3 -u manage.py shell < /tmp/create_superuser.py || true
    echo "	INFO: import cid10"
    python -u manage.py import_icd_cid --file icd10cid10v2017.csv || true
    
    mkdir static || true
    echo "	INFO: colectstatic"
    python3 -u manage.py collectstatic --no-input || true

    echo "	INFO: populate_history"
    python3 -u manage.py populate_history --auto || true
    
    
    rm /tmp/create_superuser.py
    
    # If NES was installed from a release it won"t have a .git directory
    chown -R vscode $NES_DIR/.git || true
    chown -R vscode $NES_DIR/patientregistrationsystem
    
    touch $NES_DIR/.nes_initialization.placeholder
    chown -R nobody $NES_DIR/.nes_initialization.placeholder
fi

echo "INFO: Done initializing data"

echo "entrypoint.sh finished"

exec "$@"
