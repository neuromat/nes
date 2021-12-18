FROM python:3.8-alpine3.12 as wheeler
ENV PYTHONUNBUFFERED=1


RUN apk update && \
	apk add --no-cache \
		libpng-dev \
		freetype-dev \
		build-base \
		git \
		# The limesurvey version compatible with NES isn't compatible with Postgresql11+ \\
		postgresql-bdr-dev \
		openblas-dev \
		libjpeg-turbo-dev \
        libc6-compat \
		hdf5-dev && \
	rm -rf /var/cache/apk/* && \
	ln -s /usr/include/locale.h /usr/include/xlocale.h \

# For Work with DCM2BIDS
RUN apk --update add libstdc++ curl ca-certificates && \
        curl -sSL https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.34-r0/glibc-2.34-r0.apk -o /tmp/glibc-2.34-r0.apk && \
        curl -sSL https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.34-r0/glibc-bin-2.34-r0.apk -o /tmp/glibc-bin-2.34-r0.apk && \
        apk add --allow-untrusted /tmp/*.apk && \
        rm -v /tmp/*.apk && \
        /usr/glibc-compat/sbin/ldconfig /lib /usr/glibc-compat/lib && \
    wget https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20211006/dcm2niix_lnx.zip -P /tmp && \
    unzip /tmp/dcm2niix_lnx.zip -d /usr/bin/.


ARG NES_TAG=unset
ARG NES_BRANCH=unset
ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR

RUN mkdir -p "$NES_DIR"  && \
		if [ "$NES_TAG" != "unset" ]; then \
			echo Cloning tag "$NES_TAG" ;\
			wget https://github.com/neuromat/nes/archive/TAG-"${NES_TAG}".tar.gz -qO - | \
				tar xzv --strip-components=1 -C "$NES_DIR" ;\
			sed -i 's/\(psycopg2==\)[0-9.]\+/\12.7.5/' /nes/patientregistrationsystem/qdc/requirements.txt ;\
			sed -i '1isetuptools>=40.6.3' /nes/patientregistrationsystem/qdc/requirements.txt ;\
			sed -i '1ipip>=18.1' /nes/patientregistrationsystem/qdc/requirements.txt ;\
			echo 'mne>=0.17.0' >> /nes/patientregistrationsystem/qdc/requirements.txt ;\
			echo 'pydicom>=2.2.0' >> /nes/patientregistrationsystem/qdc/requirements.txt ;\
            echo 'dcm2bids>=2.1.6' >> /nes/patientregistrationsystem/qdc/requirements.txt ;\
			echo '-e "git+https://github.com/AllenInstitute/nwb-api.git#egg=nwb&subdirectory=ainwb"' >> /nes/patientregistrationsystem/qdc/requirements.txt ;\
		elif [ "$NES_BRANCH" != "unset" ]; then \
			echo Cloning "$NES_BRANCH" branch ;\
			git clone -j $(nproc) -b "$NES_BRANCH"  https://github.com/neuromat/nes.git "$NES_DIR" ;\
		else \
			echo Cloning master branch ;\
			git clone -j $(nproc) https://github.com/neuromat/nes.git "$NES_DIR" ;\
		fi

RUN mkdir -p /wheels/requirement && \
	cp "$NES_DIR"/patientregistrationsystem/qdc/requirements.txt /wheels/requirement

WORKDIR /wheels

RUN pip3 install -U pip setuptools wheel && \
	pip3 install -r requirement/requirements.txt && \
	pip3 wheel -r requirement/requirements.txt

FROM alpine:3.12

SHELL ["/bin/sh","-exc"]

RUN apk update && \
	apk add --no-cache \
		# Postgresql 9, due to LS incompatbilities \\
		postgresql-bdr \
		postgresql-bdr-client \
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
		py3-pip \
		# supervisord  \\
		supervisor \
		# nes dependencies \\
		graphviz \
		openblas-dev \
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
ARG LIMESURVEY_URL_DOWNLOAD=https://github.com/LimeSurvey/LimeSurvey/archive/2.73.1+171220.tar.gz
ARG LIMESURVEY_DIR=/var/www/limesurvey
ENV LIMESURVEY_DIR=$LIMESURVEY_DIR

RUN mkdir -p "$LIMESURVEY_DIR" && \
		wget "$LIMESURVEY_URL_DOWNLOAD" -qO - | \
			tar xz --strip-components=1 -C "$LIMESURVEY_DIR" && \
		chown -R apache:apache "$LIMESURVEY_DIR" && \
		chmod -R o-rwx "$LIMESURVEY_DIR" && \
		chmod -R 770 "${LIMESURVEY_DIR}"/application/config/ && \
		chmod -R 770 "${LIMESURVEY_DIR}"/upload/ && \
		chmod -R 770 "${LIMESURVEY_DIR}"/tmp/ && \
		mkdir -p /run/apache2

VOLUME $LIMESURVEY_DIR

# NES INSTALLATION ###########################################################
ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR

COPY --from=wheeler /wheels /wheels

COPY --from=wheeler $NES_DIR $NES_DIR

RUN pip3 install -U pip setuptools wheel && \
	pip3 install -r /wheels/requirement/requirements.txt -f /wheels && \
		rm -rf /wheels && \
		rm -rf /root/.cache/pip*

VOLUME $NES_DIR

# RUN ###########################################################
ENV SUPERVISOR_CONF_DIR=${SUPERVISOR_CONF_DIR:-"/etc/supervisor"}

# This problem is probably related to alpine:3.12 python version:
# https://stackoverflow.com/questions/60588431/psycopg2-import-error-ssl-check-private-key-symbol-not-found     
ENV LD_PRELOAD='/lib/libssl.so.1.1'


COPY ./entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

CMD [ "/bin/sh", "-c", "/usr/bin/supervisord -c ${SUPERVISOR_CONF_DIR}/supervisord.conf" ]
