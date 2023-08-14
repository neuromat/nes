FROM mcr.microsoft.com/devcontainers/python:1-3.10-bookworm

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=dialog

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get -y update --no-install-recommends && \
    apt-get -y install --no-install-recommends \
    python3-dev \
    python-dev-is-python3 \
    python-is-python3 \
    python3-pip \
    libpng-dev \
    libpq-dev \
    #freetype-dev \
    #build-base \
    git \
    postgresql\
    #openblas-dev \
    libjpeg-dev \
    #hdf5-dev && \
    apache2 \
    libapache2-mod-wsgi-py3 \
    netcat-traditional \
    graphviz && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists* && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h


# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
COPY $NES_DIR/patientregistrationsystem/qdc/requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# Limesurvey
ARG LIMESURVEY_VERSION=5.6.32+230731
ARG LIMESURVEY_URL_DOWNLOAD=https://github.com/LimeSurvey/LimeSurvey/archive/$LIMESURVEY_VERSION.tar.gz
ARG LIMESURVEY_DIR=/var/www/limesurvey
ENV LIMESURVEY_DIR=$LIMESURVEY_DIR

RUN apt-get -y update --no-install-recommends && \
    apt-get -y install --no-install-recommends \
    wget \
    php \
    php-pgsql \
    php-gd \
    php-imap \
    php-mbstring \
    php-ldap \
    php-zip \
    php-xml && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists*

RUN mkdir -p "$LIMESURVEY_DIR" && \
    wget "$LIMESURVEY_URL_DOWNLOAD" -qO - | \
    tar xz --strip-components=1 -C "$LIMESURVEY_DIR" && \
    useradd apache && \
    chown -R apache:apache "$LIMESURVEY_DIR" && \
    chmod -R o-rwx "$LIMESURVEY_DIR" && \
    chmod -R 770 "${LIMESURVEY_DIR}"/application/config/ && \
    chmod -R 770 "${LIMESURVEY_DIR}"/upload/ && \
    chmod -R 770 "${LIMESURVEY_DIR}"/tmp/ && \
    mkdir -p /run/apache2

VOLUME $LIMESURVEY_DIR

# END
ENV DEBIAN_FRONTEND=dialog



COPY .devcontainer/entrypoint.sh /

#SHELL ["/bin/sh","-exc"]
#ENTRYPOINT [ "entrypoint.sh" ]

#CMD [ "/bin/sh", "-c", "python3 -u ${NES_DIR}/patientregistrationsystem/qdc/manage.py runserver -v3 $NES_IP:$NES_PORT" ]