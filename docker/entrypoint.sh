#!/bin/sh

set -e

PGDATA=${PGDATA:-"/var/lib/postgresql/data"}

# LIMESURVEY
## SYSTEM OPTIONS
LIMESURVEY_HOST=${LIMESURVEY_HOST:-"localhost"}
LIMESURVEY_PORT=${LIMESURVEY_PORT:-"8080"}
LIMESURVEY_DIR="$LIMESURVEY_DIR"
APACHE2_CONF_DIR="${LIMESURVEY_DIR}/application/config"
## CONFIG.PHP OPTIONS
LIMESURVEY_DB_HOST=${LIMESURVEY_DB_HOST:-"localhost"}
LIMESURVEY_DB_PORT=${LIMESURVEY_DB_PORT:-"5432"}
LIMESURVEY_DB=${LIMESURVEY_DB:-"limesurvey_db"}
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
## SYSTEM OPTIONS (set on Docker build)
NES_DIR=$NES_DIR
## SETTINGS_LOCAL OPTIONS
### DJANGO
NES_SECRET_KEY=${NES_SECRET_KEY:-"your_secret_key"}
NES_ADMIN_USER=${NES_ADMIN_USER:-"nes_admin"}
NES_ADMIN_EMAIL=${NES_ADMIN_EMAIL:-"nes_admin@nesmail.false"}
NES_ADMIN_PASSWORD=${NES_ADMIN_PASSWORD:-"nes_admin_password"}
NES_IP=${NES_IP:-0.0.0.0}
NES_PORT=${NES_PORT:-8000}
### DB
NES_DB_HOST=${NES_DB_HOST:-"localhost"}
NES_DB=${NES_DB:-"nes_db"}
NES_DB_PORT=${NES_DB_PORT:-"5432"}
NES_DB_USER=${NES_DB_USER:-"nes_user"}
NES_DB_PASSWORD=${NES_DB_PASSWORD:-"nes_password"}

# SUPERVISOR
SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/etc/supervisor"}

# Entrypoint only variables
NES_PROJECT_PATH="${NES_DIR}/patientregistrationsystem/qdc"
NES_SETUP_PATH="${NES_PROJECT_PATH}/qdc"

# INITIALIZE POSTGRESQL ##################################################
if [ -s "$PGDATA/PG_VERSION" ]
then
	echo "INFO: Database already initialized"
else
	echo "INFO: Initializing postgres database"
	cd / && su postgres -c "pg_ctl init -D $PGDATA"
	echo "host all all all md5" >> "${PGDATA}"/pg_hba.conf
fi

# LIMESURVEY SETUP ####################################################

if [ -f "${LIMESURVEY_DIR}"/application/config/config.php ]
then
	echo "INFO: LimeSurvey config.php already provisioned"
else
	cd "$LIMESURVEY_DIR"
	echo "INFO: Creating LimeSurvey configuration"
	cp application/config/config-sample-pgsql.php application/config/config.php
	sed -i "s#\('connectionString' => \).*,\$#\\1'pgsql:host=${LIMESURVEY_DB_HOST};port=${LIMESURVEY_DB_PORT};dbname=${LIMESURVEY_DB};',#g" application/config/config.php
	sed -i "s#\('username' => \).*,\$#\\1'${LIMESURVEY_DB_USER}',#g" application/config/config.php
	sed -i "s#\('password' => \).*,\$#\\1'${LIMESURVEY_DB_PASSWORD}',#g" application/config/config.php
	sed -i "s#\('charset' => \).*,\$#\\1'${LIMESURVEY_DB_CHARSET}',#g" application/config/config.php
	sed -i "s#\('tablePrefix' => \).*,\$#\\1'${LIMESURVEY_DB_TABLE_PREFIX}',#g" application/config/config.php
	sed -i "s#\('urlFormat' => \).*,\$#\\1'${LIMESURVEY_URL_FORMAT}',#g" application/config/config.php
fi

# Makes sure that JSON-RPC interface will be available
cd "$LIMESURVEY_DIR"
sed -i "s#\(\$config\['RPCInterface'\]\ =\ \).*;\$#\\1'json';#g" application/config/config-defaults.php

if [ -f "${APACHE2_CONF_DIR}"/httpd.conf ]
then
	echo "INFO: LimeSurvey-Apache configuration already provisioned"
else
	echo "INFO: Creating Apache2 configuration"
	mkdir -p "$APACHE2_CONF_DIR"

	cat <<-EOF > "${APACHE2_CONF_DIR}"/httpd.conf
		ServerTokens Prod
		PidFile /tmp/httpd.pid
		ServerRoot /var/www
		Listen $LIMESURVEY_PORT

		ServerSignature Off

		LoadModule authn_file_module modules/mod_authn_file.so
		LoadModule authn_core_module modules/mod_authn_core.so
		LoadModule authz_host_module modules/mod_authz_host.so
		LoadModule authz_groupfile_module modules/mod_authz_groupfile.so
		LoadModule authz_user_module modules/mod_authz_user.so
		LoadModule authz_core_module modules/mod_authz_core.so
		LoadModule access_compat_module modules/mod_access_compat.so
		LoadModule auth_basic_module modules/mod_auth_basic.so
		LoadModule reqtimeout_module modules/mod_reqtimeout.so
		LoadModule filter_module modules/mod_filter.so
		LoadModule mime_module modules/mod_mime.so
		LoadModule log_config_module modules/mod_log_config.so
		LoadModule env_module modules/mod_env.so
		LoadModule headers_module modules/mod_headers.so
		LoadModule setenvif_module modules/mod_setenvif.so
		LoadModule version_module modules/mod_version.so
		LoadModule mpm_prefork_module modules/mod_mpm_prefork.so
		LoadModule unixd_module modules/mod_unixd.so
		LoadModule status_module modules/mod_status.so
		LoadModule autoindex_module modules/mod_autoindex.so
		LoadModule dir_module modules/mod_dir.so
		LoadModule alias_module modules/mod_alias.so
		LoadModule rewrite_module modules/mod_rewrite.so
		LoadModule negotiation_module modules/mod_negotiation.so
		LoadModule expires_module modules/mod_expires.so

		LoadModule php7_module modules/mod_php7.so

		<IfModule unixd_module>
		  		User apache
		  		Group apache
		</IfModule>

		<IfModule dir_module>
		    DirectoryIndex /index.php index.php index.html
		</IfModule>

		# ServerName limesurvey.example.com

		DocumentRoot $LIMESURVEY_DIR
		<Directory />
		    AllowOverride None
		    Require all denied
		</Directory>

		<Directory $LIMESURVEY_DIR>
		    Options Indexes FollowSymLinks MultiViews
		    AllowOverride None
		    Require all granted
		    AcceptPathInfo On
		</Directory>

		<Files ".ht*">
		    Require all denied
		</Files>

		ErrorLog /dev/stdout
		ErrorLogFormat "[%t] [%l] [pid %P] %F: %E: [client %a] %M"

		LogLevel info
		<IfDefine LOGDEBUG>
		    LogLevel debug
		</IfDefine>

		<IfModule log_config_module>
		    LogFormat "[%{%a %b %d %H:%M:%S %Y}t] [access] [pid %P] %h %l %u %r %>s %b (%Ts)" access_log
		    CustomLog "/dev/stdout" access_log
		</IfModule>

		TypesConfig /etc/apache2/mime.types
		AddType application/x-compress .Z
		AddType application/x-gzip .gz .tgz
		AddType application/x-httpd-php php
		AddType application/x-httpd-php-source phps

		<IfModule mime_magic_module>
		MIMEMagicFile /etc/apache2/magic
		</IfModule>
	EOF
	chown -R apache:apache "$APACHE2_CONF_DIR"
fi

# NES SETUP ###########################################################
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
fi

# INITIALIZE DATA ####################################################

if [ -f "${PGDATA}"/.db_users.placeholder ]
then
	echo "INFO: DB users already provisioned"
else
	echo "INFO: Creating users in postgres"
	cd /
	su postgres -c "pg_ctl start -w -D $PGDATA"
	cat <<-EOF | su postgres -c "psql"
		CREATE USER $NES_DB_USER WITH PASSWORD '$NES_DB_PASSWORD' ;
		CREATE DATABASE $NES_DB OWNER $NES_DB_USER ;
		GRANT ALL PRIVILEGES ON DATABASE $NES_DB TO $NES_DB_USER ;
		ALTER ROLE $NES_DB_USER WITH CREATEDB;
		CREATE USER $LIMESURVEY_DB_USER WITH PASSWORD '$LIMESURVEY_DB_PASSWORD' ;
		CREATE DATABASE $LIMESURVEY_DB OWNER $LIMESURVEY_DB_USER ;
		GRANT ALL PRIVILEGES ON DATABASE $LIMESURVEY_DB TO $LIMESURVEY_DB_USER ;
	EOF
	su postgres -c "pg_ctl stop -w -D $PGDATA"
	touch "${PGDATA}"/.db_users.placeholder
fi

if [ -f "${LIMESURVEY_DIR}"/.limesurvey_superuser.placeholder ]
then
	echo "INFO: LimeSurvey superuser already provisioned"
else
	echo "INFO: Creating superuser in LimeSurvey"
	su postgres -c "pg_ctl start -w -D $PGDATA"
	cd "$LIMESURVEY_DIR"
	php7 application/commands/console.php install \
		"$LIMESURVEY_ADMIN_USER" \
		"$LIMESURVEY_ADMIN_PASSWORD" \
		"$LIMESURVEY_ADMIN_NAME" \
		"$LIMESURVEY_ADMIN_EMAIL"
	cd / && su postgres -c "pg_ctl stop -w -D $PGDATA"
	touch "${LIMESURVEY_DIR}"/.limesurvey_superuser.placeholder
fi

if [ -f "${NES_DIR}"/.nes_initialization.placeholder ]
then
	echo "INFO: NES data has already been initialized"
else
	echo "INFO: Initializing NES data (migrations, initial, superuser,ICD)"
	cd "$NES_PROJECT_PATH"
	cat <<-EOF > /tmp/create_superuser.py
		from django.contrib.auth import get_user_model
		User = get_user_model()
		User.objects.create_superuser("$NES_ADMIN_USER", "$NES_ADMIN_EMAIL", "$NES_ADMIN_PASSWORD")
	EOF

	su postgres -c "pg_ctl start -w -D $PGDATA"
	python3 -u manage.py migrate
	# Different versions may have different commannds
	python3 -u manage.py shell < add_initial_data.py || true
	python3 -u manage.py loaddata load_initial_data.json || true
	python3 -u manage.py shell < /tmp/create_superuser.py || true
	python3 -u manage.py import_icd_cid --file icd10cid10v2017.csv || true
	python3 -u manage.py createcachetable|| true

	rm /tmp/create_superuser.py

	# If NES was installed from a release it won't have a .git directory 
	chown -R nobody "${NES_DIR}"/.git  || true
	chown -R nobody "${NES_DIR}"/patientregistrationsystem

	su postgres -c "pg_ctl stop -w -D $PGDATA"
	touch "${NES_DIR}"/.nes_initialization.placeholder
fi

# SUPERVISOR SETUP ####################################################

if [ -f "${SUPERVISOR_CONF_DIR}"/supervisord.conf ]
then
	echo "INFO: Supervisord configuration file already provisioned"
else
	echo "INFO: Creating Supervisord configuration file"
	mkdir -p "$SUPERVISOR_CONF_DIR"
	cat <<-EOF > "${SUPERVISOR_CONF_DIR}"/supervisord.conf
		[supervisord]
		nodaemon=true
		loglevel=debug
		logfile=/dev/null
		nocleanup=true

		[program:postgresql]
		command=/usr/bin/postgres -D $PGDATA
		user=postgres
		stopsignal=INT ; based on supervisord docs
		priority=0 ; must start before the others
		autostart=true
		autorestart=true
		redirect_stderr=true
		stdout_logfile=/dev/pts/0
		stdout_logfile_maxbytes=0

		[program:limesurvey]
		command=/usr/sbin/httpd -D FOREGROUND -f $APACHE2_CONF_DIR/httpd.conf
		priority=1 ; must start after the database
		autostart=true
		autorestart=true
		stopasgroup=true
		redirect_stderr=true
		stdout_logfile=/dev/pts/0
		stdout_logfile_maxbytes=0

		[program:nes]
		; This way we trick django into thinking its running on a tty and skip error-prone git checks
		command=sh -c 'GIT_PYTHON_REFRESH=quiet /usr/bin/python3 $NES_PROJECT_PATH/manage.py runserver -v3 $NES_IP:$NES_PORT > /dev/pts/0'
		user=nobody
		priority=2 ; must start after limesurvey
		autostart=true
		autorestart=true
		stopasgroup=true
		redirect_stderr=true
		stdout_logfile=/dev/pts/0
		stdout_logfile_maxbytes=0
		environment=HOME="$NES_DIR"
	EOF
fi

# Enables django runserver to write its logs to stdout
chmod a+w /dev/pts/0

exec "$@"
