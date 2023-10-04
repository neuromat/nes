FROM python:3.11-slim-bookworm as wheeler

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND dialog

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  


ARG DEBUG
ARG NES_BRANCH=dev
ARG NES_DIR=usr/local/nes
ENV NES_DIR=$NES_DIR


RUN apt-get -y update --no-install-recommends && \
    apt-get -y install --no-install-recommends \
    python3-dev \
    python-is-python3 \
    python3-pip \
    pip \
    libjpeg-dev \
    libpng-dev \
    libpq-dev \
    libfreetype6-dev \
    zlib1g-dev \
    g++ \
    make \
    #freetype-dev \
    #build-base \
    git && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists* && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN mkdir -p $NES_DIR  && \
    if [ $NES_BRANCH != "unset" ]; then \
        echo Cloning $NES_BRANCH branch ;\
        git clone -j $(nproc) -b "$NES_BRANCH"  https://github.com/mcostat/nes.git $NES_DIR ;\
    else \
        echo Cloning master branch ;\
        git clone -j $(nproc) https://github.com/mcostat/nes.git $NES_DIR ;\
    fi


RUN mkdir -p /wheels/requirement && \
    cp $NES_DIR/patientregistrationsystem/qdc/requirements.txt /wheels/requirement

WORKDIR /wheels

RUN pip3 install -U pip setuptools wheel && \
    pip3 install -r requirement/requirements.txt && \
    pip3 wheel -r requirement/requirements.txt


FROM python:3.11-slim-bookworm
ENV DEBIAN_FRONTEND dialog

ARG NES_DIR=usr/local/nes
ENV NES_DIR=$NES_DIR

RUN apt-get -y update --no-install-recommends && \
    apt-get -y install --no-install-recommends \
    curl \
    python3-psycopg2 \
    python-is-python3 \
    python3-pip \
    pip \
    libnss3-tools \
    git \
    apache2 \
    locales \
    openssl \
    libapache2-mod-wsgi-py3 \
    netcat-traditional \
    # server dependencies
    #libopenblas-dev \
    #libhdf5-dev \
    graphviz && \
    #snapd && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists* && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h

COPY --from=wheeler /wheels /wheels

COPY --from=wheeler $NES_DIR $NES_DIR

RUN pip3 install -U pip setuptools wheel && \
	pip3 install -r /wheels/requirement/requirements.txt -f /wheels && \
		rm -rf /wheels && \
		rm -rf /root/.cache/pip*

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

RUN sed -i -e 's/Listen 80/Listen 80\nServerName localhost/' /etc/apache2/ports.conf

# Setup certbot for automatic SSL certificates
# RUN service snap start && \
#     snap install --classic certbot && \
#     ln -s /snap/bin/certbot /usr/bin/certbot

# RUN python3 -m venv /opt/certbot/ && \
#     /opt/certbot/bin/pip install --upgrade pip && \
#     /opt/certbot/bin/pip install certbot certbot-apache && \
#     ln -s /opt/certbot/bin/certbot /usr/bin/certbot 

RUN curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64" && \
    chmod +x mkcert-v*-linux-amd64 && \
    cp mkcert-v*-linux-amd64 /usr/local/bin/mkcert && \
    /usr/local/bin/mkcert -install

WORKDIR /usr/local/nes

RUN cp docker/entrypoint.sh / && \
    chmod +x /entrypoint.sh 
    

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/bin/bash", "-c", "service apache2 start"]

