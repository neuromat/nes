#!/bin/sh

set -ex

# ENVIRONMENT#################################################

PGDATA=${PGDATA:-'/var/lib/postgresql/data'}

LIMESURVEY_HOST=${LIMESURVEY_HOST:-'localhost'}
LIMESURVEY_PORT=${LIMESURVEY_PORT:-'8080'}

LIMESURVEY_DB_HOST=${LIMESURVEY_DB_HOST:-'localhost'}
LIMESURVEY_DB_PORT=${LIMESURVEY_DB_PORT:-'5432'}
LIMESURVEY_DB=${LIMESURVEY_DB:-'limesurvey_db'}
LIMESURVEY_DB_TABLE_PREFIX=${LIMESURVEY_DB_TABLE_PREFIX:-'lime_'}
LIMESURVEY_DB_USER=${LIMESURVEY_DB_USER:-'limesurvey_user'}
LIMESURVEY_DB_PASSWORD=${LIMESURVEY_DB_PASSWORD:-'limesurvey_password'}
LIMESURVEY_DB_CHARSET=${LIMESURVEY_DB_CHARSET:-'utf8'}

LIMESURVEY_ADMIN_USER=${LIMESURVEY_ADMIN_USER:-'limesurvey_admin'}
LIMESURVEY_ADMIN_NAME=${LIMESURVEY_ADMIN_NAME:-'limesurvey_admin_name'}
LIMESURVEY_ADMIN_EMAIL=${LIMESURVEY_ADMIN_EMAIL:-'limesurvey@limemail.false'}
LIMESURVEY_ADMIN_PASSWORD=${LIMESURVEY_ADMIN_PASSWORD:-'limesurvey_admin_password'}

LIMESURVEY_URL_FORMAT=${LIMESURVEY_URL_FORMAT:-'path'}

LIMESURVEY_CONF_DIR=${LIMESURVEY_CONF_DIR:-'/httpd_config'}
LIMESURVEY_URL_DOWNLOAD=${LIMESURVEY_URL_DOWNLOAD:-'https://github.com/LimeSurvey/LimeSurvey/archive/2.73.0+171219.tar.gz'}
LIMESURVEY_DIR=${LIMESURVEY_DIR:-'/var/www/limesurvey'}

NES_DIR=${NES_DIR:-'/nes'}
NES_PROJECT_PATH="$NES_DIR"/patientregistrationsystem/qdc
NES_SETUP_PATH="$NES_PROJECT_PATH"/qdc


NES_DB_TYPE=${NES_DB_TYPE:-'pgsql'}
NES_DB_HOST=${NES_DB_HOST:-'localhost'}
NES_DB=${NES_DB:-'nes_db'}
NES_DB_PORT=${NES_DB_PORT:-'5432'}
NES_DB_USER=${NES_DB_USER:-'nes_user'}
NES_DB_PASSWORD=${NES_DB_PASSWORD:-'nes_password'}

# NES specific settings
NES_SECRET_KEY=${NES_SECRET_KEY:-'your_secret_key'}
NES_ADMIN_USER=${NES_ADMIN_USER:-'nes_admin'}
NES_ADMIN_EMAIL=${NES_ADMIN_EMAIL:-'nes_admin@nesmail.false'}
NES_ADMIN_PASSWORD=${NES_ADMIN_PASSWORD:-'nes_admin_password'}
NES_IP=${NES_IP:-0.0.0.0}
NES_PORT=${NES_PORT:-8000}

# SETUP POSTGRESQL##################################################
apk add --no-cache postgresql

mkdir -p /var/run/postgresql
chown -R postgres:postgres /var/run/postgresql
chmod 2777 /var/run/postgresql

mkdir -p "$PGDATA"
chown -R postgres:postgres "$PGDATA"
chmod 700 "$PGDATA"

su postgres -c "pg_ctl init -D $PGDATA"
echo "host all all all md5" >> "$PGDATA"/pg_hba.conf

#SETUP LIMESURVEY####################################################
apk add --no-cache \
	php7 \
	php7-session \
	php7-pdo_pgsql \
	php7-gd \
	php7-imap \
	php7-mbstring \
	php7-ldap \
	php7-zip \
	php7-xml \
	php7-simplexml \
	php7-apache2 \
	php7-json \
	php7-ctype \
	apache2

apk --no-cache add aria2 curl
aria2c -x16  "$LIMESURVEY_URL_DOWNLOAD"
apk del aria2 curl
tar xzf LimeSurvey*
rm LimeSurvey*.tar.gz
mkdir -p "$(dirname "$LIMESURVEY_DIR")"
mv LimeSurvey* "$LIMESURVEY_DIR"

cd "$LIMESURVEY_DIR"

cp application/config/config-sample-pgsql.php application/config/config.php
sed -i "s#\('connectionString' => \).*,\$#\\1'pgsql:host=${LIMESURVEY_DB_HOST};port=${LIMESURVEY_DB_PORT};dbname=${LIMESURVEY_DB};',#g" application/config/config.php
sed -i "s#\('username' => \).*,\$#\\1'${LIMESURVEY_DB_USER}',#g" application/config/config.php
sed -i "s#\('password' => \).*,\$#\\1'${LIMESURVEY_DB_PASSWORD}',#g" application/config/config.php
sed -i "s#\('charset' => \).*,\$#\\1'${LIMESURVEY_DB_CHARSET}',#g" application/config/config.php
sed -i "s#\('tablePrefix' => \).*,\$#\\1'${LIMESURVEY_DB_TABLE_PREFIX}',#g" application/config/config.php
sed -i "s#\('urlFormat' => \).*,\$#\\1'${LIMESURVEY_URL_FORMAT}',#g" application/config/config.php
sed -i "s#\($config\['RPCInterface'\]\ =\ \).*;\$#\\1'json';#g" application/config/config-defaults.php

chown -R apache:apache "$LIMESURVEY_DIR"
chmod -R o-rwx "$LIMESURVEY_DIR"
chmod -R 770 "$LIMESURVEY_DIR"/application/config/
chmod -R 770 "$LIMESURVEY_DIR"/upload/
chmod -R 770 "$LIMESURVEY_DIR"/tmp/
mkdir -p /run/apache2
mkdir -p "$LIMESURVEY_CONF_DIR"
chown -R apache:apache "$LIMESURVEY_CONF_DIR"

cat <<-EOCONF > "$LIMESURVEY_CONF_DIR"/httpd.conf
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

	ServerName limesurvey.example.com

	DocumentRoot "$LIMESURVEY_DIR"

	<Directory />
	    AllowOverride None
	    Require all denied
	</Directory>

	<Directory "$LIMESURVEY_DIR">
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

EOCONF

#SETUP NES###########################################################

apk add --no-cache \
	libpng-dev \
	freetype-dev \
	build-base \
	git \
	postgresql-dev \
	openblas-dev \
	libjpeg-turbo-dev \
	python3-dev

# Fix locale lib expected path
ln -s /usr/include/locale.h /usr/include/xlocale.h

# Install hdf5-dev that is only available in the testing repo
echo 'http://linorg.usp.br/AlpineLinux/edge/testing' >> /etc/apk/repositories
apk update
apk add --no-cache hdf5-dev
sed -i '$ d' /etc/apk/repositories

mkdir -p "$NES_DIR"
git clone -j "$(nproc)"  https://github.com/neuromat/nes.git "$NES_DIR"

cd "$NES_PROJECT_PATH"
pip3 install -r requirements.txt


cat <<-EOF > "$NES_SETUP_PATH"/wsgi.py
	import os
	import sys
	import site
	paths = ['/usr/local', '/nes', '/nes/patientregistrationsystem', '/nes/patientregistrationsystem/qdc',]
	for path in paths:
	    if path not in sys.path:
	        sys.path.append(path)
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings")
	from django.core.wsgi import get_wsgi_application
	application = get_wsgi_application()
EOF

cat <<-EOF > "$NES_SETUP_PATH"/settings_local.py
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

chown -R nobody "$NES_DIR"/.git
chown -R nobody "$NES_DIR"/patientregistrationsystem


#INITIALIZE DATA####################################################

su postgres -c "pg_ctl start -D $PGDATA"

echo "CREATE USER $NES_DB_USER WITH PASSWORD '$NES_DB_PASSWORD' ;
	CREATE DATABASE $NES_DB OWNER $NES_DB_USER ;
	GRANT ALL PRIVILEGES ON DATABASE $NES_DB TO $NES_DB_USER ;
	ALTER ROLE $NES_DB_USER WITH CREATEDB;
	" | su postgres -c "psql"

echo "CREATE USER $LIMESURVEY_DB_USER WITH PASSWORD '$LIMESURVEY_DB_PASSWORD' ;
	CREATE DATABASE $LIMESURVEY_DB OWNER $LIMESURVEY_DB_USER ;
	GRANT ALL PRIVILEGES ON DATABASE $LIMESURVEY_DB TO $LIMESURVEY_DB_USER ;
	ALTER ROLE $LIMESURVEY_DB_USER WITH CREATEDB;
	" | su postgres -c "psql"

cd "$LIMESURVEY_DIR"
php7 application/commands/console.php install "$LIMESURVEY_ADMIN_USER" "$LIMESURVEY_ADMIN_PASSWORD" "$LIMESURVEY_ADMIN_NAME" "$LIMESURVEY_ADMIN_EMAIL"

cd "$NES_PROJECT_PATH"
cat <<-EOF > /tmp/create_superuser.py
	from django.contrib.auth import get_user_model
	User = get_user_model()
	User.objects.create_superuser('$NES_ADMIN_USER', '$NES_ADMIN_EMAIL', '$NES_ADMIN_PASSWORD')
EOF

python3 manage.py migrate
python3 manage.py shell < add_initial_data.py
python3 manage.py loaddata load_initial_data.json
python3 manage.py shell < /tmp/create_superuser.py

rm /tmp/create_superuser.py

su postgres -c "pg_ctl stop -D $PGDATA"

# SUPERVISOR####################################################
apk add --no-cache supervisor
cat <<-EOF > /etc/supervisord.conf
	[supervisord]
	nodaemon=true
	loglevel=info
	logfile=/dev/null

	[program:postgresql]
	command=/usr/bin/postgres -D $PGDATA
	user=postgres
	stopsignal=INT ; based on supervisord docs
	priority=0 ; must start before the others
	autostart=true
	autorestart=true
	redirect_stderr=true
	stdout_logfile=/dev/fd/1
	stdout_logfile_maxbytes=0

	[program:limesurvey]
	command=/usr/sbin/httpd -D FOREGROUND -f $LIMESURVEY_CONF_DIR/httpd.conf
	priority=1 ; must start after the database
	autostart=true
	autorestart=true
	redirect_stderr=true
	stdout_logfile=/dev/fd/1
	stdout_logfile_maxbytes=0

	[program:nes]
	command=/usr/bin/python3 $NES_PROJECT_PATH/manage.py runserver $NES_IP:$NES_PORT
	user=nobody
	priority=2 ; must start after limesurvey
	autostart=true
	autorestart=true
	redirect_stderr=true
	stdout_logfile=/dev/fd/1
	stdout_logfile_maxbytes=0
	environment=HOME="$NES_DIR"
EOF
