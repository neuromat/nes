FROM alpine:3.8

SHELL ["/bin/sh","-exc"]

# POSTGRES
ENV PGDATA=${PGDATA:-"/var/lib/postgresql/data"} \
# LIMESURVEY
## SYSTEM OPTIONS
		LIMESURVEY_HOST=${LIMESURVEY_HOST:-"localhost"} \
		LIMESURVEY_PORT=${LIMESURVEY_PORT:-"8080"} \
		LIMESURVEY_URL_DOWNLOAD=${LIMESURVEY_URL_DOWNLOAD:-"https://github.com/LimeSurvey/LimeSurvey/archive/2.73.0+171219.tar.gz"} \
		LIMESURVEY_DIR=${LIMESURVEY_DIR:-"/var/www/limesurvey"} \
		LIMESURVEY_CONF_DIR=${LIMESURVEY_CONF_DIR:-"/httpd_config"} \
## CONFIG.PHP OPTIONS
		LIMESURVEY_DB_HOST=${LIMESURVEY_DB_HOST:-"localhost"} \
		LIMESURVEY_DB_PORT=${LIMESURVEY_DB_PORT:-"5432"} \
		LIMESURVEY_DB=${LIMESURVEY_DB:-"limesurvey_db"} \
		LIMESURVEY_DB_TABLE_PREFIX=${LIMESURVEY_DB_TABLE_PREFIX:-"lime_"} \
		LIMESURVEY_DB_USER=${LIMESURVEY_DB_USER:-"limesurvey_user"} \
		LIMESURVEY_DB_PASSWORD=${LIMESURVEY_DB_PASSWORD:-"limesurvey_password"} \
		LIMESURVEY_DB_CHARSET=${LIMESURVEY_DB_CHARSET:-"utf8"} \
		LIMESURVEY_URL_FORMAT=${LIMESURVEY_URL_FORMAT:-"path"} \
## SUPER USER CREATION OPTION
		LIMESURVEY_ADMIN_USER=${LIMESURVEY_ADMIN_USER:-"limesurvey_admin"} \
		LIMESURVEY_ADMIN_NAME=${LIMESURVEY_ADMIN_NAME:-"limesurvey_admin_name"} \
		LIMESURVEY_ADMIN_EMAIL=${LIMESURVEY_ADMIN_EMAIL:-"limesurvey@limemail.false"} \
		LIMESURVEY_ADMIN_PASSWORD=${LIMESURVEY_ADMIN_PASSWORD:-"limesurvey_admin_password"} \
# NES
## SYSTEM OPTIONS
		NES_DIR=${NES_DIR:-"/nes"} \
		NES_PROJECT_PATH=${NES_PROJECT_PATH:-"/nes/patientregistrationsystem/qdc"} \
		NES_SETUP_PATH=${NES_SETUP_PATH:-"/nes/patientregistrationsystem/qdc/qdc"} \
## SETTINGS_LOCAL OPTIONS
### DB
		NES_DB_TYPE=${NES_DB_TYPE:-"pgsql"} \
		NES_DB_HOST=${NES_DB_HOST:-"localhost"} \
		NES_DB=${NES_DB:-"nes_db"} \
		NES_DB_PORT=${NES_DB_PORT:-"5432"} \
		NES_DB_USER=${NES_DB_USER:-"nes_user"} \
		NES_DB_PASSWORD=${NES_DB_PASSWORD:-"nes_password"} \
### DJANGO
		NES_SECRET_KEY=${NES_SECRET_KEY:-"your_secret_key"} \
		NES_ADMIN_USER=${NES_ADMIN_USER:-"nes_admin"} \
		NES_ADMIN_EMAIL=${NES_ADMIN_EMAIL:-"nes_admin@nesmail.false"} \
		NES_ADMIN_PASSWORD=${NES_ADMIN_PASSWORD:-"nes_admin_password"} \
		NES_IP=${NES_IP:-0.0.0.0} \
		NES_PORT=${NES_PORT:-8000}

RUN apk update && \
		apk add --no-cache \
# postgres
		postgresql \
# limesurvey - apache2
		apache2 \
# limesurvey - php
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
# git to clone and update nes
		git \
# libs to build django extensions
		libpng-dev \
		freetype-dev \
		build-base \
		postgresql-dev \
		openblas-dev \
		libjpeg-turbo-dev \
		python3-dev \
# supervisord
		supervisor

# Fixes to get testing packages and to make locale lib available
RUN echo 'http://linorg.usp.br/AlpineLinux/edge/testing' >> /etc/apk/repositories && \
		apk update && \
		apk add --no-cache hdf5-dev && \
		sed -i '$ d' /etc/apk/repositories && \
		ln -s /usr/include/locale.h /usr/include/xlocale.h

# SETUP POSTGRESQL ##################################################
RUN	mkdir -p /var/run/postgresql  && \
		chown -R postgres:postgres /var/run/postgresql  && \
		chmod 2777 /var/run/postgresql  && \
		mkdir -p "$PGDATA"  && \
		chown -R postgres:postgres "$PGDATA"  && \
		chmod 700 "$PGDATA"  && \
		su postgres -c "pg_ctl init -D "$PGDATA""  && \
		echo -e "\nhost all all all md5" >> "$PGDATA"/pg_hba.conf

# LIMESURVEY INSTALLATION ####################################################
RUN apk --no-cache add aria2 && \
		aria2c -x16  "$LIMESURVEY_URL_DOWNLOAD" && \
		apk del aria2 && \
		tar xzf LimeSurvey* && \
		rm LimeSurvey*.tar.gz && \
		mkdir -p $(dirname "$LIMESURVEY_DIR") && \
		mv LimeSurvey* "$LIMESURVEY_DIR"

# LIMESURVEY SETUP ####################################################
WORKDIR $LIMESURVEY_DIR

RUN cp application/config/config-sample-pgsql.php application/config/config.php  && \
		sed -i "s#\('connectionString' => \).*,\$#\\1'pgsql:host=${LIMESURVEY_DB_HOST};port=${LIMESURVEY_DB_PORT};dbname=${LIMESURVEY_DB};',#g" application/config/config.php && \
		sed -i "s#\('username' => \).*,\$#\\1'${LIMESURVEY_DB_USER}',#g" application/config/config.php  && \
		sed -i "s#\('password' => \).*,\$#\\1'${LIMESURVEY_DB_PASSWORD}',#g" application/config/config.php  && \
		sed -i "s#\('charset' => \).*,\$#\\1'${LIMESURVEY_DB_CHARSET}',#g" application/config/config.php  && \
		sed -i "s#\('tablePrefix' => \).*,\$#\\1'${LIMESURVEY_DB_TABLE_PREFIX}',#g" application/config/config.php  && \
		sed -i "s#\('urlFormat' => \).*,\$#\\1'${LIMESURVEY_URL_FORMAT}',#g" application/config/config.php  && \
		sed -i "s#\($config\['RPCInterface'\]\ =\ \).*;\$#\\1'json';#g" application/config/config-defaults.php  && \
		chown -R apache:apache "$LIMESURVEY_DIR" && \
		chmod -R o-rwx "$LIMESURVEY_DIR" && \
		chmod -R 770 "$LIMESURVEY_DIR"/application/config/ && \
		chmod -R 770 "$LIMESURVEY_DIR"/upload/ && \
		chmod -R 770 "$LIMESURVEY_DIR"/tmp/ && \
		mkdir -p /run/apache2 && \
		mkdir -p "$LIMESURVEY_CONF_DIR" && \
		chown -R apache:apache "$LIMESURVEY_CONF_DIR" && \
		echo $'\
			ServerTokens Prod \n\
			PidFile /tmp/httpd.pid \n\
			ServerRoot /var/www \n\
			Listen '$LIMESURVEY_PORT$'\n\
			\n\
			ServerSignature Off \n\
			\n\
			LoadModule authn_file_module modules/mod_authn_file.so \n\
			LoadModule authn_core_module modules/mod_authn_core.so \n\
			LoadModule authz_host_module modules/mod_authz_host.so \n\
			LoadModule authz_groupfile_module modules/mod_authz_groupfile.so \n\
			LoadModule authz_user_module modules/mod_authz_user.so \n\
			LoadModule authz_core_module modules/mod_authz_core.so \n\
			LoadModule access_compat_module modules/mod_access_compat.so \n\
			LoadModule auth_basic_module modules/mod_auth_basic.so \n\
			LoadModule reqtimeout_module modules/mod_reqtimeout.so \n\
			LoadModule filter_module modules/mod_filter.so \n\
			LoadModule mime_module modules/mod_mime.so \n\
			LoadModule log_config_module modules/mod_log_config.so \n\
			LoadModule env_module modules/mod_env.so \n\
			LoadModule headers_module modules/mod_headers.so \n\
			LoadModule setenvif_module modules/mod_setenvif.so \n\
			LoadModule version_module modules/mod_version.so \n\
			LoadModule mpm_prefork_module modules/mod_mpm_prefork.so \n\
			LoadModule unixd_module modules/mod_unixd.so \n\
			LoadModule status_module modules/mod_status.so \n\
			LoadModule autoindex_module modules/mod_autoindex.so \n\
			LoadModule dir_module modules/mod_dir.so \n\
			LoadModule alias_module modules/mod_alias.so \n\
			LoadModule rewrite_module modules/mod_rewrite.so \n\
			LoadModule negotiation_module modules/mod_negotiation.so \n\
			LoadModule expires_module modules/mod_expires.so \n\
			\n\
			LoadModule php7_module modules/mod_php7.so \n\
			\n\
			<IfModule unixd_module> \n\
	    		User apache \n\
	    		Group apache \n\
			</IfModule> \n\
			\n\
			<IfModule dir_module>  \n\
			    DirectoryIndex /index.php index.php index.html  \n\
			</IfModule>  \n\
			\n\
			ServerName limesurvey.example.com \n\
			\n\
			DocumentRoot '$LIMESURVEY_DIR$'\n\
			<Directory /> \n\
			    AllowOverride None \n\
			    Require all denied \n\
			</Directory> \n\
			\n\
			<Directory '$LIMESURVEY_DIR$'> \n\
			    Options Indexes FollowSymLinks MultiViews \n\
			    AllowOverride None \n\
			    Require all granted \n\
			    AcceptPathInfo On \n\
			</Directory> \n\
			\n\
			<Files ".ht*"> \n\
			    Require all denied \n\
			</Files> \n\
			\n\
			ErrorLog /dev/stdout \n\
			ErrorLogFormat "[%t] [%l] [pid %P] %F: %E: [client %a] %M" \n\
			\n\
			LogLevel info \n\
			<IfDefine LOGDEBUG> \n\
			    LogLevel debug \n\
			</IfDefine> \n\
			\n\
			<IfModule log_config_module> \n\
			    LogFormat "[%{%a %b %d %H:%M:%S %Y}t] [access] [pid %P] %h %l %u %r %>s %b (%Ts)" access_log \n\
			    CustomLog "/dev/stdout" access_log \n\
			</IfModule> \n\
			\n\
			TypesConfig /etc/apache2/mime.types \n\
			AddType application/x-compress .Z \n\
			AddType application/x-gzip .gz .tgz \n\
			AddType application/x-httpd-php php \n\
			AddType application/x-httpd-php-source phps \n\
			\n\
			<IfModule mime_magic_module> \n\
			MIMEMagicFile /etc/apache2/magic \n\
			</IfModule> \n\
		' | tr -d '\t' > ${LIMESURVEY_CONF_DIR}/httpd.conf

# NES INSTALLATION ###########################################################
RUN mkdir -p $NES_DIR  && \
		git clone -j $(nproc)  https://github.com/neuromat/nes.git $NES_DIR  && \
		cd $NES_PROJECT_PATH  && \
		pip3 install -r requirements.txt

# NES SETUP ###########################################################
RUN echo $'\
			import os \n\
			import sys \n\
			import site \n\
			paths = ["'$NES_PROJECT_PATH$'", "'$NES_DIR$'", "/usr/local", "/usr/bin", "/bin",] \n\
			for path in paths: \n\
	    		if path not in sys.path: \n\
	        		sys.path.append(path) \n\
			os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings") \n\
			from django.core.wsgi import get_wsgi_application \n\
			application = get_wsgi_application() \n\
		' | tr -d '\t' > ${NES_SETUP_PATH}/wsgi.py && \
		echo $'\
			SECRET_KEY = "'$NES_SECRET_KEY$'"  \n\
			DEBUG = True  \n\
			DEBUG404 = True  \n\
			TEMPLATE_DEBUG = DEBUG  \n\
			IS_TESTING = False  \n\
			ALLOWED_HOSTS = ["'$NES_IP$'"]  \n\
			DATABASES = {  \n\
			    "default": {  \n\
			        "ENGINE": "django.db.backends.postgresql_psycopg2",  \n\
			        "NAME": "'$NES_DB$'",  \n\
			        "USER": "'$NES_DB_USER$'",  \n\
			        "PASSWORD": "'$NES_DB_PASSWORD$'",  \n\
			        "HOST": "'$NES_DB_HOST$'",  \n\
			        "PORT": "'$NES_DB_PORT$'", # default port  \n\
			    }  \n\
			}  \n\
			LIMESURVEY = {  \n\
			    "URL_API": "http://'$LIMESURVEY_HOST$':'$LIMESURVEY_PORT$'",  \n\
			    "URL_WEB": "http://'$LIMESURVEY_HOST$':'$LIMESURVEY_PORT$'",  \n\
			    "USER": "'$LIMESURVEY_ADMIN_USER$'",  \n\
			    "PASSWORD": "'$LIMESURVEY_ADMIN_PASSWORD$'"  \n\
			}  \n\
			LOGO_INSTITUTION = "logo-institution.png"  \n\
		' | tr -d '\t' > ${NES_SETUP_PATH}/settings_local.py && \
		chown -R nobody ${NES_DIR}/.git && \
		chown -R nobody ${NES_DIR}/patientregistrationsystem

# INITIALIZE DATA ####################################################
RUN	su postgres -c "pg_ctl start -D "$PGDATA"" && \
		echo $'\
			CREATE USER '$NES_DB_USER$' WITH PASSWORD '"'"''$NES_DB_PASSWORD$''"'"' ; \
			CREATE DATABASE '$NES_DB$' OWNER '$NES_DB_USER$' ; \
			GRANT ALL PRIVILEGES ON DATABASE '$NES_DB$' TO '$NES_DB_USER$' ; \
			ALTER ROLE '$NES_DB_USER$' WITH CREATEDB; \
			' | su postgres -c "psql" && \
		echo $'\
			CREATE USER '$LIMESURVEY_DB_USER$' WITH PASSWORD '"'"''$LIMESURVEY_DB_PASSWORD$''"'"' ; \
			CREATE DATABASE '$LIMESURVEY_DB$' OWNER '$LIMESURVEY_DB_USER$' ; \
			GRANT ALL PRIVILEGES ON DATABASE '$LIMESURVEY_DB$' TO '$LIMESURVEY_DB_USER$' ; \
			' | su postgres -c "psql" && \
		cd $LIMESURVEY_DIR && \
		php7 application/commands/console.php install $LIMESURVEY_ADMIN_USER $LIMESURVEY_ADMIN_PASSWORD $LIMESURVEY_ADMIN_NAME $LIMESURVEY_ADMIN_EMAIL && \
		cd $NES_PROJECT_PATH && \
		echo $'\
			from django.contrib.auth import get_user_model \n\
			User = get_user_model() \n\
			User.objects.create_superuser("'$NES_ADMIN_USER$'", "'$NES_ADMIN_EMAIL$'", "'$NES_ADMIN_PASSWORD$'") \n\
		' | tr -d '\t' > /tmp/create_superuser.py && \
		cat qdc/settings_local.py && \
		cat qdc/wsgi.py && \
		python3 manage.py migrate && \
		python3 manage.py shell < add_initial_data.py && \
		python3 manage.py loaddata load_initial_data.json && \
		python3 manage.py shell < /tmp/create_superuser.py && \
		rm /tmp/create_superuser.py && \
		su postgres -c "pg_ctl stop -D "$PGDATA""

# SUPERVISOR SETUP ####################################################
RUN echo $'\
		[supervisord] \n\
		nodaemon=true \n\
		loglevel=info \n\
		logfile=/dev/null \n\
		 \n\
		[program:postgresql] \n\
		command=/usr/bin/postgres -D '$PGDATA$' \n\
		user=postgres \n\
		stopsignal=INT ; based on supervisord docs \n\
		priority=0 ; must start before the others \n\
		autostart=true \n\
		autorestart=true \n\
		redirect_stderr=true \n\
		stdout_logfile=/dev/fd/1 \n\
		stdout_logfile_maxbytes=0 \n\
		 \n\
		[program:limesurvey] \n\
		command=/usr/sbin/httpd -D FOREGROUND -f '$LIMESURVEY_CONF_DIR$'/httpd.conf \n\
		priority=1 ; must start after the database \n\
		autostart=true \n\
		autorestart=true \n\
		redirect_stderr=true \n\
		stdout_logfile=/dev/fd/1 \n\
		stdout_logfile_maxbytes=0 \n\
		 \n\
		[program:nes] \n\
		command=/usr/bin/python3 '$NES_PROJECT_PATH$'/manage.py runserver '$NES_IP$':'$NES_PORT$' \n\
		user=nobody \n\
		priority=2 ; must start after limesurvey \n\
		autostart=true \n\
		autorestart=true \n\
		redirect_stderr=true \n\
		stdout_logfile=/dev/fd/1 \n\
		stdout_logfile_maxbytes=0 \n\
		environment=HOME="'$NES_DIR$'" \n\
		' | tr -d '\t' > /etc/supervisord.conf

# RUN ###########################################################
WORKDIR $NES_PROJECT_PATH

CMD ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]
