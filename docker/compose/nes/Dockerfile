# sudo docker build -t nes:test -f docker/compose/nes/Dockerfile .
# sudo docker run --rm -it nes:test /bin/bash
# ----------------------------
FROM python:3.8-slim as wheeler
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		git \
		build-essential \
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
# FROM alpine:3.12

# SHELL ["/bin/sh","-exc"]

# RUN apk update && \
# 	apk add --no-cache \
# 		git \
# 		libpq \
# 		openblas-dev \
# 		libjpeg-turbo-dev \
# 		python3 \
# 		py3-pip \
# 		graphviz \
# 		hdf5-dev && \
# 	rm -rf /var/cache/apk/*

# ARG NES_DIR=/nes
# ENV NES_DIR=$NES_DIR

# COPY --from=wheeler /wheels /wheels

# COPY --from=wheeler $NES_DIR $NES_DIR

# RUN pip3 install -U pip setuptools wheel && \
# 	pip3 install -r /wheels/requirement/requirements.txt -f /wheels && \
# 		rm -rf /wheels && \
# 		rm -rf /root/.cache/pip*

# VOLUME $NES_DIR

# COPY ./entrypoint.sh /

# ENV NES_IP ${NES_IP:-0.0.0.0}
# ENV NES_PORT ${NES_PORT:-8000}

# ENTRYPOINT [ "/entrypoint.sh" ]

# CMD [ "/bin/sh", "-c", "/usr/bin/python3 -u ${NES_DIR}/patientregistrationsystem/qdc/manage.py runserver -v3 $NES_IP:$NES_PORT" ]
