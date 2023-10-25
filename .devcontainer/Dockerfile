FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

# Keeps Python from generating .pyc files in the container
#ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8


RUN apt-get -y update --no-install-recommends && export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install --no-install-recommends \
    python-is-python3 \
    python3-dev \
    libjpeg-dev \
    libpng-dev \
    libpq-dev \
    libfreetype6-dev \
    #build-base \
    git \
    #openblas-dev \
    #hdf5-dev && \
    apache2 \
    libapache2-mod-wsgi-py3 \
    netcat-traditional \
    lsb-release \
    curl \
    gpg \
    graphviz && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    # Remove imagemagick due to https://security-tracker.debian.org/tracker/CVE-2019-10131
    apt-get purge -y imagemagick imagemagick-6-common && \
    rm -rf /var/lib/apt/lists* && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h


RUN curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list && \
    apt-get -y update --no-install-recommends && export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install --no-install-recommends redis


COPY $NES_DIR/patientregistrationsystem/qdc/requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# COPY $NES_DIR/patientregistrationsystem/qdc/src/nwb/dist/nwb-1.0.0-py3-none-any.whl .
# RUN pip3 --disable-pip-version-check install nwb-1.0.0-py3-none-any.whl \
#     && rm nwb-1.0.0-py3-none-any.whl

ENV DEBIAN_FRONTEND=dialog

COPY .devcontainer/entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
