# sudo docker build -t nes:test -f docker/compose/nes/Dockerfile .
# sudo docker run --rm -it nes:test /bin/bash
FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1

SHELL ["/bin/sh","-exc"]

# System deps (build + runtime together)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        build-essential \
        python3-distutils \
        libpq-dev \
        libpq5 \
        libopenblas-dev \
        libjpeg62-turbo-dev \
        libpng-dev \
        libfreetype6-dev \
        graphviz \
        libhdf5-dev && \
    rm -rf /var/lib/apt/lists/*

# App location
ENV NES_DIR=/nes
WORKDIR $NES_DIR

RUN git config --global --add safe.directory /nes

# App source
COPY . .

# Python deps
RUN pip install --no-cache-dir \
    -r patientregistrationsystem/qdc/requirements.txt

# Runtime config
ENV NES_IP=0.0.0.0
ENV NES_PORT=8000

COPY docker/compose/nes/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

# CMD ["/bin/sh", "-c", "python -u patientregistrationsystem/qdc/manage.py runserver -v3 $NES_IP:$NES_PORT"]
