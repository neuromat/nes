FROM mcr.microsoft.com/devcontainers/python:3.10-bookworm

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=dialog

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get -y update --no-install-recommends && \
    apt-get -y install --no-install-recommends \
    python-is-python3 \
    python3-pip \
    libpng-dev \
    libpq-dev \
    #freetype-dev \
    #build-base \
    git \
    postgresql \
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

# END
ENV DEBIAN_FRONTEND=dialog


COPY .devcontainer/entrypoint.sh /

RUN sudo chmod 777 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

SHELL ["/bin/sh", "-c"]
CMD [ "$NES_DIR/scripts/init_data.sh" ]
