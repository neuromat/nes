FROM python:3.11-bookworm

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND dialog

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  


ARG DEBUG
ARG NES_BRANCH=dev
ARG NES_DIR=usr/local/nes


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
    #freetype-dev \
    #build-base \
    git \
    #openblas-dev \
    #hdf5-dev && \
    apache2 \
    locales \
    libapache2-mod-wsgi-py3 \
    netcat-traditional \
    graphviz && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists* && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

RUN sed -i -e 's/Listen 80/Listen 80\nServerName localhost/' /etc/apache2/ports.conf

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

WORKDIR /usr/local/nes

#RUN cp $NES_DIR/docker/entrypoint.sh / && \
RUN chmod +x docker/entrypoint.sh

ENTRYPOINT ["docker/entrypoint.sh"]

CMD ["/bin/bash", "-c", "a2dissite 000-default.conf; a2ensite nes; service apache2 restart"]

