FROM python:3.11-bookworm

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND dialog

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

ARG NES_BRANCH=dev
ARG NES_DIR=/usr/local/nes

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
    libapache2-mod-wsgi-py3 \
    netcat-traditional \
    graphviz && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists* && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h


RUN mkdir -p $NES_DIR  && \
    git clone -j $(nproc) -b $NES_BRANCH  https://github.com/mcostat/nes.git $NES_DIR;


COPY $NES_DIR/patientregistrationsystem/qdc/requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

COPY $NES_DIR/patientregistrationsystem/qdc/src/nwb/dist/nwb-1.0.0-py3-none-any.whl .
RUN pip3 --disable-pip-version-check install nwb-1.0.0-py3-none-any.whl \
    && rm nwb-1.0.0-py3-none-any.whl


COPY /entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT /entrypoint.sh
