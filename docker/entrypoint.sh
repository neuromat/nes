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
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings.prod")
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
		        "ENGINE": "django.db.backends.postgresql",
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

        # Settings to send emails
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "$EMAIL_HOST_USER"
EMAIL_HOST_PASSWORD = "$EMAIL_HOST_PASSWORD"
DEFAULT_FROM_EMAIL = "$EMAIL_HOST_USER"
SERVER_EMAIL = EMAIL_HOST_USER
		LOGO_INSTITUTION = "$NES_PROJECT_PATH/logo-institution.png"
	EOF
    chown -R nobody $NES_PROJECT_PATH/qdc/settings/settings_local.py

    touch $NES_PROJECT_PATH/nes_settings.placeholder
    chown -R nobody $NES_PROJECT_PATH/nes_settings.placeholder

    echo "criou arquivos de config"
fi

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
    echo "	INFO: create_super_ser.py"
    python3 -u manage.py shell < /tmp/create_superuser.py || true
    echo "	INFO: import cid10"
    python3 -u manage.py import_icd_cid --file icd10cid10v2017.csv || true
    
    mkdir static || true
    echo "	INFO: colectstatic"
    python3 -u manage.py collectstatic --no-input || true

    echo "	INFO: populate_history"
    python3 -u manage.py populate_history --auto || true

    mkdir -p $NES_PROJECT_PATH/media/eeg_electrode_system_files/1/
    mkdir -p $NES_PROJECT_PATH/media/eeg_electrode_system_files/2/
    mkdir -p $NES_PROJECT_PATH/media/eeg_electrode_system_files/3/
    
    cp -r $NES_PROJECT_PATH/site_static/imgs/International_10-10_system_for_EEG.png $NES_PROJECT_PATH/media/eeg_electrode_system_files/2/International_10-10_system_for_EEG.png
    cp -r $NES_PROJECT_PATH/site_static/imgs/International_10-20_system_for_EEG.jpg $NES_PROJECT_PATH/media/eeg_electrode_system_files/3/International_10-20_system_for_EEG.jpg
    cp -r $NES_PROJECT_PATH/site_static/imgs/128_channel_HCGSN_v.1.0.png $NES_PROJECT_PATH/media/eeg_electrode_system_files/1/128_channel_HCGSN_v.1.0.png

    
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
    mkdir -p /etc/apache2/ssl-certs
    cat <<-EOF >/etc/apache2/sites-available/nes.conf
<VirtualHost *:$NES_PORT>
    ServerName $NES_IP
    ServerAlias $NES_HOSTNAME
    ServerAdmin lapis@peb.ufrj.br

    DocumentRoot $NES_PROJECT_PATH

    <Directory />
        Options FollowSymLinks
        AllowOverride None
    </Directory>

    Alias /media/ $NES_PROJECT_PATH/media/
    Alias /static/ $NES_PROJECT_PATH/static/

    <Directory $NES_PROJECT_PATH/media>
        Require all granted
    </Directory>

    <Directory $NES_PROJECT_PATH/static>
        Require all granted
    </Directory>

    <Directory $NES_PROJECT_PATH>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    WSGIScriptAlias / $NES_PROJECT_PATH/qdc/wsgi.py application-group=%{GLOBAL}
    WSGIDaemonProcess nes lang='en_US.UTF-8' locale='en_US.UTF-8'
    WSGIProcessGroup nes

    ErrorLog ${APACHE_LOG_DIR}/nes_error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/nes_access.log combined
</VirtualHost>
	EOF

    cat <<-EOF >/etc/apache2/sites-available/nes-ssl.conf
<IfModule mod_ssl.c>
<VirtualHost *:443>
    Protocols h2 h2c http/1.1

    ServerName $NES_IP
    ServerAlias $NES_HOSTNAME
    ServerAdmin lapis@peb.ufrj.br

    DocumentRoot $NES_PROJECT_PATH

    <Directory />
        Options FollowSymLinks
        AllowOverride None
    </Directory>

    Alias /media/ $NES_PROJECT_PATH/media/
    Alias /static/ $NES_PROJECT_PATH/static/

    <Directory $NES_PROJECT_PATH/media>
        Require all granted
    </Directory>

    <Directory $NES_PROJECT_PATH/static>
        Require all granted
    </Directory>

    <Directory $NES_PROJECT_PATH>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    #Alias /img/ $NES_PROJECT_PATH/img/

    WSGIScriptAlias / $NES_PROJECT_PATH/qdc/wsgi.py application-group=%{GLOBAL}
    WSGIDaemonProcess nes-ssl lang='en_US.UTF-8' locale='en_US.UTF-8'
    WSGIProcessGroup nes-ssl

    SSLEngine on
 
    SSLCertificateFile  /etc/apache2/ssl-certs/cert.pem
    SSLCertificateKeyFile /etc/apache2/ssl-certs/key.pem
 
    <FilesMatch "\.(cgi|shtml|phtml|php)$">
            SSLOptions +StdEnvVars
    </FilesMatch>
    <Directory /usr/lib/cgi-bin>
            SSLOptions +StdEnvVars
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/nes_ssl_error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/nes_ssl_access.log combined
</VirtualHost>
</IfModule>
	EOF

    mkcert -key-file /etc/apache2/ssl-certs/key.pem -cert-file /etc/apache2/ssl-certs/cert.pem $NES_HOSTNAME $NES_IP localhost 0.0.0.0

    a2enmod ssl
    a2enmod http2
    a2dissite 000-default.conf
    a2ensite nes
    a2ensite nes-ssl
fi

echo "INFO: Done initializing data"

echo "INFO: Starting Redis"
echo never > /sys/kernel/mm/transparent_hugepage/enabled 
service redis-server start

echo "INFO: Starting Apache"
service apache2 start

echo "INFO: entrypoint.sh finished"

exec "$@"

