# sudo docker build -t nes:test -f docker/compose/nes/Dockerfile .
# sudo docker run --rm -it nes:test /bin/bash
# ----------------------------
FROM python:3.8-slim as builder
ENV PYTHONUNBUFFERED=1

# TODO: clean up unnecessary packages
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

ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR
WORKDIR $NES_DIR

COPY . .

RUN pip install -r "$NES_DIR"/patientregistrationsystem/qdc/requirements.txt

# ----------------------------
FROM python:3.8-slim

ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR
WORKDIR $NES_DIR

SHELL ["/bin/sh","-exc"]

# TODO: clean up unnecessary packages
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

COPY --from=builder /usr/local /usr/local
COPY --from=builder $NES_DIR $NES_DIR

ENV NES_IP=${NES_IP:-0.0.0.0}
ENV NES_PORT=${NES_PORT:-8000}

COPY ./docker/compose/nes/entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

CMD [ "/bin/sh", "-c", "/usr/bin/python3 -u ${NES_DIR}/patientregistrationsystem/qdc/manage.py runserver -v3 $NES_IP:$NES_PORT" ]
