FROM python:3.11-bookworm

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=dialog

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

ARG NES_DIR="/workspaces/nes"
ARG NES_BRANCH="dev"

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get -y update --no-install-recommends && \
    apt-get -y install --no-install-recommends \
    python3-dev \
    python-is-python3 \
    python3-pip \
    pip \
    libpng-dev \
    libpq-dev \
    #freetype-dev \
    #build-base \
    git \
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


RUN mkdir -p $NES_DIR  && \
    git clone -j $(nproc) -b $NES_BRANCH  https://github.com/mcostat/nes.git $NES_DIR;

# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
COPY $NES_DIR/patientregistrationsystem/qdc/requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# END
ENV DEBIAN_FRONTEND=dialog

EXPOSE 80

COPY .devcontainer/entrypoint.sh /
RUN sudo chmod 777 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
