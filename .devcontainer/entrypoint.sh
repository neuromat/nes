#!/bin/sh
set -e

PGDATA=${PGDATA:-"/var/lib/postgresql/data"}

# LIMESURVEY
## SYSTEM OPTIONS
LIMESURVEY_HOST=${LIMESURVEY_HOST:-"localhost"}
LIMESURVEY_PORT=${LIMESURVEY_PORT:-"80"}
LIMESURVEY_DIR=$LIMESURVEY_DIR
APACHE2_CONF_DIR="${LIMESURVEY_DIR}/application/config"
## CONFIG.PHP OPTIONS
LIMESURVEY_DB_TYPE=${LIMESURVEY_DB_TYPE:-"pgsql"}
LIMESURVEY_DB_HOST=${LIMESURVEY_DB_HOST:-"db"}
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
LIMESURVEY_ADMIN_EMAIL=${LIMESURVEY_ADMIN_EMAIL:-"admin@limesurvey.false"}
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
NES_DB_HOST=${NES_DB_HOST:-"db"}
NES_DB_PORT=${NES_DB_PORT:-"5432"}
NES_DB=${NES_DB:-"nes_db"}
NES_DB_USER=${NES_DB_USER:-"nes_user"}
NES_DB_PASSWORD=${NES_DB_PASSWORD:-"nes_password"}

# SUPERVISOR
#SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/etc/supervisor"}

# Entrypoint only variables
NES_PROJECT_PATH="${NES_DIR}/patientregistrationsystem/qdc"
NES_SETUP_PATH="${NES_PROJECT_PATH}/qdc"

if [ "$NES_DB_TYPE" != "pgsql" ]; then
	echo "Unfortunately, for the time being, NES only works with PostgreSQL."
	exit 1
fi

# LIMESURVEY SETUP ####################################################
if [ -f /etc/apache2/sites-available/limesurvey.conf ]; then
	echo "INFO: LimeSurvey-Apache configuration already provisioned"
else
	echo "INFO: Creating Apache2 configuration"
	mkdir -p "$APACHE2_CONF_DIR"

	cat <<-EOF >"/etc/apache2/sites-available/limesurvey.conf"
		<VirtualHost localhost:80>
			ServerName limesurvey.example.com

			DocumentRoot /var/www/limesurvey

			<Directory />
					Options FollowSymLinks
					AllowOverride None
			</Directory>

			<Directory /var/www/limesurvey>
					Options Indexes FollowSymLinks MultiViews
					AllowOverride None
					Order allow,deny
					Allow from all
					AcceptPathInfo On
			</Directory>

			ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/

			<Directory "/usr/lib/cgi-bin">
					AllowOverride None
					Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
					Order allow,deny
					Allow from all
			</Directory>

			ErrorLog ${APACHE_LOG_DIR}/limesurvey_error.log
			LogLevel warn
			CustomLog ${APACHE_LOG_DIR}/limesurvey_access.log combined
		</VirtualHost>
	EOF

	echo "ServerName 127.0.0.1" >> /etc/apache2/apache2.conf

fi

while ! nc -z "$LIMESURVEY_DB_HOST" "$LIMESURVEY_DB_PORT"; do
	sleep 0.2
done

if [ -f "${LIMESURVEY_DIR}"/application/config/config.php ]; then
	echo "INFO: LimeSurvey config.php already provisioned"
else
	cd "$LIMESURVEY_DIR"
	echo "INFO: Creating LimeSurvey configuration"

	if [ $LIMESURVEY_DB_TYPE = "mysql" ]; then
		echo "INFO: Using MySQL configuration"
		LIMESURVEY_DB_CHARSET=${LIMESURVEY_DB_CHARSET:-"utf8mb4"}
		cp application/config/config-sample-mysql.php application/config/config.php
	elif [ $LIMESURVEY_DB_TYPE = "pgsql" ]; then
		echo "INFO: Using PostgreSQL configuration"
		LIMESURVEY_DB_CHARSET=${LIMESURVEY_DB_CHARSET:-"utf8"}
		cp application/config/config-sample-pgsql.php application/config/config.php
	else
		echo "Error: unrecognized LIMESURVEY_DB_TYPE: '$LIMESURVEY_DB_TYPE'"
		exit 1
	fi

	echo "INFO: Using TCP connection"
	sed -i "s#\("connectionString" => \).*,\$#\\1'pgsql:host=${LIMESURVEY_DB_HOST};port=${LIMESURVEY_DB_PORT};dbname=${LIMESURVEY_DB};',#g" application/config/config.php
	sed -i "s#\("username" => \).*,\$#\\1'${LIMESURVEY_DB_USER}',#g" application/config/config.php
	sed -i "s#\("password" => \).*,\$#\\1'${LIMESURVEY_DB_PASSWORD}',#g" application/config/config.php
	sed -i "s#\("charset" => \).*,\$#\\1'${LIMESURVEY_DB_CHARSET}',#g" application/config/config.php
	sed -i "s#\("tablePrefix" => \).*,\$#\\1'${LIMESURVEY_DB_TABLE_PREFIX}',#g" application/config/config.php
	sed -i "s#\("urlFormat" => \).*,\$#\\1'${LIMESURVEY_URL_FORMAT}',#g" application/config/config.php

	# Makes sure that JSON-RPC interface will be available
	sed -i "s#\(\$config\["RPCInterface"\]\ =\ \).*;\$#\\1"json";#g" application/config/config-defaults.php

	# Check if LIMESURVEY_DB_PASSWORD is set
	if [ -z "$LIMESURVEY_DB_PASSWORD" ]; then
		echo >&2 "Error: Missing LIMESURVEY_DB_PASSWORD"
		exit 1
	fi

	# Check if LIMESURVEY_DB_PASSWORD is set
	if [ -z "$LIMESURVEY_ADMIN_PASSWORD" ]; then
		echo >&2 "Error: Missing LIMESURVEY_ADMIN_PASSWORD"
		exit 1
	fi

	echo "INFO: Running console.php install"
	echo su apache -c php "${LIMESURVEY_DIR}"/application/commands/console.php install $LIMESURVEY_ADMIN_USER $LIMESURVEY_ADMIN_PASSWORD $LIMESURVEY_ADMIN_NAME $LIMESURVEY_ADMIN_EMAIL

	#su apache -c php "${LIMESURVEY_DIR}"/application/commands/console.php install $LIMESURVEY_ADMIN_USER $LIMESURVEY_ADMIN_PASSWORD $LIMESURVEY_ADMIN_NAME $LIMESURVEY_ADMIN_EMAIL
fi

# NES SETUP ####################################################
if [ -f "${NES_SETUP_PATH}"/wsgi.py ]; then
	echo "INFO: NES wsgi.py file already provisioned"
else
	echo "INFO: Creating NES wsgi.py file"
	cat <<-EOF >"${NES_SETUP_PATH}"/wsgi.py
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

if [ -f "${NES_SETUP_PATH}"/settings_local.py ]; then
	echo "INFO: NES settings_local.py file already provisioned"
else
	echo "INFO: Creating NES settings_local.py file"
	cat <<-EOF >"${NES_SETUP_PATH}"/settings_local.py
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

while ! nc -z "$NES_DB_HOST" "$NES_DB_PORT"; do
	sleep 0.2
done

# INITIALIZE DATA ####################################################

## PG DB
# if [ -f "${PGDATA}"/.db_users.placeholder ]; then
# 	echo "INFO: DB users already provisioned"
# else
# 	echo "INFO: Creating users in postgres"
# 	cd /
# 	su postgres -c "psql start -w -D $PGDATA"
# 	cat <<-EOF | su postgres -c "psql"
# 		CREATE USER $NES_DB_USER WITH PASSWORD "$NES_DB_PASSWORD" ;
# 		CREATE DATABASE $NES_DB OWNER $NES_DB_USER ;
# 		GRANT ALL PRIVILEGES ON DATABASE $NES_DB TO $NES_DB_USER ;
# 		ALTER ROLE $NES_DB_USER WITH CREATEDB;
# 		CREATE USER $LIMESURVEY_DB_USER WITH PASSWORD "$LIMESURVEY_DB_PASSWORD" ;
# 		CREATE DATABASE $LIMESURVEY_DB OWNER $LIMESURVEY_DB_USER ;
# 		GRANT ALL PRIVILEGES ON DATABASE $LIMESURVEY_DB TO $LIMESURVEY_DB_USER ;
# 	EOF
# 	su postgres -c "psql stop -w -D $PGDATA"
# 	touch "${PGDATA}"/.db_users.placeholder
# fi

# ## Limesurvey
# if [ -f "${LIMESURVEY_DIR}"/.limesurvey_superuser.placeholder ]; then
# 	echo "INFO: LimeSurvey superuser already provisioned"
# else
# 	echo "INFO: Creating superuser in LimeSurvey"
# 	su postgres -c "psql start -w -D $PGDATA"
# 	cd "$LIMESURVEY_DIR"
# 	php7 application/commands/console.php install \
# 		"$LIMESURVEY_ADMIN_USER" \
# 		"$LIMESURVEY_ADMIN_PASSWORD" \
# 		"$LIMESURVEY_ADMIN_NAME" \
# 		"$LIMESURVEY_ADMIN_EMAIL"
# 	cd / && su postgres -c "psql stop -w -D $PGDATA"
# 	touch "${LIMESURVEY_DIR}"/.limesurvey_superuser.placeholder
#fi

## NES
if [ -f "${NES_DIR}"/.nes_initialization.placeholder ]; then
	echo "INFO: NES data has already been initialized"
else
	echo "INFO: Initializing NES data (migrations, initial, superuser, ICD)"
	cd "$NES_PROJECT_PATH"

	cat <<-EOF >/tmp/create_superuser.py
		from django.contrib.auth import get_user_model
		User = get_user_model()
		User.objects.create_superuser("$NES_ADMIN_USER", "$NES_ADMIN_EMAIL", "$NES_ADMIN_PASSWORD")
	EOF

	echo "	INFO:Migrate"
	python3 -u manage.py migrate
	# Different versions may have different commands
	echo "	INFO:add_initial_data.py"
	python3 -u manage.py shell <add_initial_data.py || true
	echo "	INFO:load_initial_data.py"
	python3 -u manage.py loaddata load_initial_data.json || true
	echo "	INFO:create_super_ser.py"
	python3 -u manage.py shell </tmp/create_superuser.py || true
	echo "	INFO:import cid10"
	python3 -u manage.py import_icd_cid --file icd10cid10v2017.csv || true
	echo "	INFO:createcachetable"
	python3 -u manage.py createcachetable || true

	rm /tmp/create_superuser.py

	# If NES was installed from a release it won"t have a .git directory
	chown -R nobody "${NES_DIR}"/.git || true
	chown -R nobody "${NES_DIR}"/patientregistrationsystem

	touch "${NES_DIR}"/.nes_initialization.placeholder
fi

# Enables django runserver to write its logs to stdout
#chmod a+w /dev/pts/0

exec "$@"
