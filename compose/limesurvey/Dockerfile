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

ARG LIMESURVEY_URL_DOWNLOAD=https://github.com/LimeSurvey/LimeSurvey/archive/2.73.0+171219.tar.gz
ARG LIMESURVEY_DIR=/var/www/limesurvey
ENV LIMESURVEY_DIR=$LIMESURVEY_DIR
ENV APACHE2_CONF="${LIMESURVEY_DIR}/application/config/httpd.conf"

RUN mkdir -p "$LIMESURVEY_DIR" && \
		wget "$LIMESURVEY_URL_DOWNLOAD" -qO - | \
			tar xzv --strip-components=1 -C "$LIMESURVEY_DIR"

RUN cd "$LIMESURVEY_DIR" && \
		chown -R apache:apache "$LIMESURVEY_DIR" && \
		chmod -R o-rwx "$LIMESURVEY_DIR" && \
		chmod -R 770 "${LIMESURVEY_DIR}"/application/config/ && \
		chmod -R 770 "${LIMESURVEY_DIR}"/upload/ && \
		chmod -R 770 "${LIMESURVEY_DIR}"/tmp/ && \
		mkdir /run/apache2

VOLUME $LIMESURVEY_DIR

USER apache

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD /usr/sbin/httpd -D FOREGROUND -f "$APACHE2_CONF"
