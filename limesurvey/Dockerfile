FROM alpine:3.8

RUN apk update && \
	apk --no-cache add \
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

RUN apk --no-cache add aria2 curl && \
	aria2c -x16  https://github.com/LimeSurvey/LimeSurvey/archive/2.73.0+171219.tar.gz && \
	apk del aria2 curl && \
	tar xzf LimeSurvey* && \
	rm LimeSurvey*.tar.gz && \
	mv Lime* /var/www/limesurvey

WORKDIR /var/www/limesurvey

RUN chown -R apache:apache /var/www/limesurvey && \
	chmod -R o-rwx /var/www/limesurvey && \
	chmod -R 770 /var/www/limesurvey/application/config/ && \
	chmod -R 770 /var/www/limesurvey/upload/ && \
	chmod -R 770 /var/www/limesurvey/tmp/ && \
	mkdir /run/apache2 && \
	mkdir /httpd_config && \
	chown -R apache:apache /httpd_config

USER apache

COPY entrypoint.sh /httpd_config/entrypoint.sh

ENTRYPOINT ["/httpd_config/entrypoint.sh"]

CMD [ "/usr/sbin/httpd", "-D", "FOREGROUND", "-f", "/httpd_config/httpd.conf" ]