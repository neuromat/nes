FROM alpine:3.8 as wheeler
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
		libpng-dev \
		freetype-dev \
		build-base \
		git \
		postgresql-dev \
		openblas-dev \
		libjpeg-turbo-dev \
		python3-dev && \
	apk add --no-cache \
		--repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
		hdf5-dev && \
	rm -rf /var/cache/apk/* && \
	ln -s /usr/include/locale.h /usr/include/xlocale.h && \
	git clone -j $(nproc) https://github.com/neuromat/nes.git

RUN mkdir -p /wheels/requirement && \
		cp /nes/patientregistrationsystem/qdc/requirements.txt /wheels/requirement

WORKDIR /wheels

RUN pip3 install -r requirement/requirements.txt && \
		pip3 install -U wheel && \
		pip3 wheel -r requirement/requirements.txt

FROM alpine:3.8

SHELL ["/bin/sh","-exc"]

RUN apk update && \
		apk add --no-cache \
		# postgres  \\
		postgresql \
		# limesurvey - apache2  \\
		apache2 \
		# limesurvey - php  \\
		php7 \
		php7-apache2 \
		php7-ctype \
		php7-gd \
		php7-imap \
		php7-json \
		php7-ldap \
		php7-mbstring \
		php7-pdo_pgsql \
		php7-session \
		php7-simplexml \
		php7-xml \
		php7-zip \
		# git to clone and update nes  \\
		git \
		# python to run django \\
		python3 \
		# supervisord  \\
		supervisor \
		# nes dependencies \\
		openblas-dev && \
		apk add --no-cache \
			--repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
			hdf5-dev && \
		rm -rf /var/cache/apk/*

# SETUP POSTGRESQL ##################################################
ARG PGDATA=/var/lib/postgresql/data
ENV PGDATA=$PGDATA

RUN	mkdir -p /var/run/postgresql  && \
		chown -R postgres:postgres /var/run/postgresql  && \
		chmod 2777 /var/run/postgresql  && \
		mkdir -p "$PGDATA"  && \
		chown -R postgres:postgres "$PGDATA"  && \
		chmod 700 "$PGDATA"

VOLUME $PGDATA

# LIMESURVEY INSTALLATION ####################################################
ARG LIMESURVEY_URL_DOWNLOAD=https://github.com/LimeSurvey/LimeSurvey/archive/2.73.0+171219.tar.gz
ARG LIMESURVEY_DIR=/var/www/limesurvey
ENV LIMESURVEY_DIR=$LIMESURVEY_DIR

RUN mkdir -p "$LIMESURVEY_DIR" && \
		wget "$LIMESURVEY_URL_DOWNLOAD" -qO - | \
			tar xzv --strip-components=1 -C "$LIMESURVEY_DIR" && \
		chown -R apache:apache "$LIMESURVEY_DIR" && \
		chmod -R o-rwx "$LIMESURVEY_DIR" && \
		chmod -R 770 "${LIMESURVEY_DIR}"/application/config/ && \
		chmod -R 770 "${LIMESURVEY_DIR}"/upload/ && \
		chmod -R 770 "${LIMESURVEY_DIR}"/tmp/ && \
		mkdir -p /run/apache2

VOLUME $LIMESURVEY_DIR

# NES INSTALLATION ###########################################################
ARG NES_TAG=unset
ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR

RUN mkdir -p "$NES_DIR"  && \
		if [ "$NES_TAG" = "unset" ]; then \
			git clone -j $(nproc)  https://github.com/neuromat/nes.git $NES_DIR ;\
		else \
			wget https://github.com/neuromat/nes/archive/TAG-"${NES_TAG}".tar.gz -qO - | \
				tar xzv --strip-components=1 -C "$NES_DIR"; \
		fi

COPY --from=wheeler /wheels /wheels

RUN pip3 install -r /wheels/requirement/requirements.txt -f /wheels && \
		rm -rf /wheels && \
		rm -rf /root/.cache/pip*

VOLUME $NES_DIR

# RUN ###########################################################
ENV SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/etc/supervisor"}
ARG SUPERVISOR_CONF_DIR=/etc/supervisor

COPY ./entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

CMD /usr/bin/supervisord -c "${SUPERVISOR_CONF_DIR}/supervisord.conf"
