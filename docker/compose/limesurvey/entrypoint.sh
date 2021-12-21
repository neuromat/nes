#!/bin/sh

# Based on the work of:
# Copyright (c) 2018 Markus Opolka
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Entrypoint for Docker Container

set -e

LIMESURVEY_PORT=${LIMESURVEY_PORT:-'8080'}

LIMESURVEY_DB_TYPE=${LIMESURVEY_DB_TYPE:-'psql'}
LIMESURVEY_DB_HOST=${LIMESURVEY_DB_HOST:-'db'}
LIMESURVEY_DB_PORT=${LIMESURVEY_DB_PORT:-'5432'}
LIMESURVEY_DB=${LIMESURVEY_DB:-'limesurvey_db'}
LIMESURVEY_DB_TABLE_PREFIX=${LIMESURVEY_DB_TABLE_PREFIX:-'lime_'}
LIMESURVEY_DB_USER=${LIMESURVEY_DB_USER:-'limesurvey_user'}
LIMESURVEY_DB_PASSWORD=${LIMESURVEY_DB_PASSWORD:-'limesurvey_password'}

LIMESURVEY_ADMIN_USER=${LIMESURVEY_ADMIN_USER:-'admin'}
LIMESURVEY_ADMIN_NAME=${LIMESURVEY_ADMIN_NAME:-'admin'}
LIMESURVEY_ADMIN_EMAIL=${LIMESURVEY_ADMIN_EMAIL:-'foobar@example.com'}
LIMESURVEY_ADMIN_PASSWORD=${LIMESURVEY_ADMIN_PASSWORD:-'password'}

LIMESURVEY_URL_FORMAT=${LIMESURVEY_URL_FORMAT:-'path'}

LIMESURVEY_DIR=$LIMESURVEY_DIR
APACHE2_CONF_DIR="${LIMESURVEY_DIR}/application/config"

if [ -f "${APACHE2_CONF_DIR}/httpd.conf" ]; then
	echo 'Info: httpd.conf already provisioned'
else
	echo 'Info: Generating apache configuration file'
	cat <<-EOF > "${APACHE2_CONF_DIR}/httpd.conf"
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
	EOF
	chown -R apache:apache "$APACHE2_CONF_DIR"
fi

while ! nc -z "$LIMESURVEY_DB_HOST" "$LIMESURVEY_DB_PORT"
do
	sleep 0.2
done

cd "$LIMESURVEY_DIR"

# Check if configuration already provisioned
if [ -f application/config/config.php ]; then
    echo 'Info: config.php already provisioned'
else
    echo 'Info: Generating config.php'

    if [ "$LIMESURVEY_DB_TYPE" = 'mysql' ]; then
        echo 'Info: Using MySQL configuration'
        LIMESURVEY_DB_CHARSET=${LIMESURVEY_DB_CHARSET:-'utf8mb4'}
        cp application/config/config-sample-mysql.php application/config/config.php
    elif [ "$LIMESURVEY_DB_TYPE" = 'pgsql' ]; then
        echo 'Info: Using PostgreSQL configuration'
        LIMESURVEY_DB_CHARSET=${LIMESURVEY_DB_CHARSET:-'utf8'}
        cp application/config/config-sample-pgsql.php application/config/config.php
    else
    	echo 'Error: unrecognized LIMESURVEY_DB_TYPE: "$LIMESURVEY_DB_TYPE"'
    	exit 1
    fi

    echo 'Info: Using TCP connection'
    sed -i "s#\('connectionString' => \).*,\$#\\1'${LIMESURVEY_DB_TYPE}:host=${LIMESURVEY_DB_HOST};port=${LIMESURVEY_DB_PORT};dbname=${LIMESURVEY_DB};',#g" application/config/config.php

    sed -i "s#\('username' => \).*,\$#\\1'${LIMESURVEY_DB_USER}',#g" application/config/config.php
    sed -i "s#\('password' => \).*,\$#\\1'${LIMESURVEY_DB_PASSWORD}',#g" application/config/config.php
    sed -i "s#\('charset' => \).*,\$#\\1'${LIMESURVEY_DB_CHARSET}',#g" application/config/config.php
    sed -i "s#\('tablePrefix' => \).*,\$#\\1'${LIMESURVEY_DB_TABLE_PREFIX}',#g" application/config/config.php

    # Set URL config
    sed -i "s#\('urlFormat' => \).*,\$#\\1'${LIMESURVEY_URL_FORMAT}',#g" application/config/config.php

		# Enable JSON-RPC Interface
    sed -i "s#\(\$config\['RPCInterface'\]\ =\ \).*;\$#\\1'json';#g" application/config/config-defaults.php

    # Check if LIMESURVEY_DB_PASSWORD is set
    if [ -z "$LIMESURVEY_DB_PASSWORD" ]; then
        echo >&2 'Error: Missing LIMESURVEY_DB_PASSWORD'
        exit 1
    fi

    # Check if LIMESURVEY_DB_PASSWORD is set
    if [ -z "$LIMESURVEY_ADMIN_PASSWORD" ]; then
        echo >&2 'Error: Missing LIMESURVEY_ADMIN_PASSWORD'
        exit 1
    fi

    echo 'Running console.php install'
    php7 application/commands/console.php install $LIMESURVEY_ADMIN_USER $LIMESURVEY_ADMIN_PASSWORD $LIMESURVEY_ADMIN_NAME $LIMESURVEY_ADMIN_EMAIL

fi

exec "$@"
