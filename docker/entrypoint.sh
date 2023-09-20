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
    cd $NES_PROJECT_PATH
    
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
    echo "	INFO create cachetable"
    python3 -u manage.py createcachetable || true
    echo "	INFO: create_super_ser.py"
    python3 -u manage.py shell < /tmp/create_superuser.py || true
    echo "	INFO: import cid10"
    python -u manage.py import_icd_cid --file icd10cid10v2017.csv || true
    
    mkdir static || true
    echo "	INFO: colectstatic"
    python3 -u manage.py collectstatic --no-input || true
    
    
    rm /tmp/create_superuser.py
    
    # If NES was installed from a release it won"t have a .git directory
    chown -R www-data $NES_DIR/.git || true
    chown -R www-data $NES_DIR/patientregistrationsystem
    
    touch $NES_DIR/.nes_initialization.placeholder
    chown -R nobody $NES_DIR/.nes_initialization.placeholder
fi

if [ -f /etc/apache2/sites-available/nes.conf ]; then
    echo "INFO: Apache data has already been initialized"
else
    echo "INFO: Initializing Apache data"

    cat <<-EOF >/etc/apache2/sites-available/nes.conf
<VirtualHost *:$NES_PORT>
    ServerName $NES_IP
    WSGIProcessGroup nes

    DocumentRoot $NES_PROJECT_PATH

    <Directory />
        Options FollowSymLinks
        AllowOverride None
    </Directory>

    Alias /media/ $NES_PROJECT_PATH/media/
    Alias /static/ $NES_PROJECT_PATH/static/

    <Directory "$NES_PROJECT_PATH">
        Require all granted
    </Directory>

    WSGIScriptAlias / $NES_PROJECT_PATH/qdc/wsgi.py application-group=%{GLOBAL}
    WSGIDaemonProcess nes lang='en_US.UTF-8' locale='en_US.UTF-8'

    Alias /img/ $NES_PROJECT_PATH/img/

    ErrorLog ${APACHE_LOG_DIR}/nes_ssl_error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/nes_ssl_access.log combined
</VirtualHost>
	EOF

    touch $NES_DIR/.apache.placeholder
    chown -R nobody $NES_DIR/.apache.placeholder

fi


echo "INFO: Done initializing data"

echo "entrypoint.sh finished"

exec a2dissite 000-default.conf; a2ensite nes; service apache2 restart

exec "$@"
