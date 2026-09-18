# Fase1: passo intermediário py3.10-slim. Fase6: Django 5.2 (branch).
FROM python:3.10-slim as wheeler
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		build-essential \
		git \
		libpq-dev \
		libhdf5-dev \
		libjpeg-dev \
		libpng-dev \
		libfreetype6-dev \
		libopenblas-dev \
		wget && \
	rm -rf /var/lib/apt/lists/*

ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR

# Fase6: build a partir do código local (contexto = raiz do repo) em vez de
# git clone do master remoto. O que entra na imagem é a branch atual.
COPY patientregistrationsystem /nes/patientregistrationsystem

RUN mkdir -p /wheels/requirement && \
	cp "$NES_DIR"/patientregistrationsystem/qdc/requirements.txt /wheels/requirement

WORKDIR /wheels

RUN pip3 install -U pip "setuptools<81" wheel && \
	pip3 install -r requirement/requirements.txt && \
	pip3 wheel -r requirement/requirements.txt

# Fase1: runtime alinhado ao wheeler (py3.10-slim). Fase6: Django 5.2 (branch).
FROM python:3.10-slim

SHELL ["/bin/sh","-exc"]

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		git \
		libpq5 \
		libhdf5-310 \
		libjpeg62-turbo \
		graphviz \
		netcat-openbsd && \
	rm -rf /var/lib/apt/lists/*

ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR

COPY --from=wheeler /wheels /wheels

COPY --from=wheeler $NES_DIR $NES_DIR

RUN pip3 install -U pip "setuptools<81" wheel && \
	pip3 install -r /wheels/requirement/requirements.txt -f /wheels && \
		rm -rf /wheels && \
		rm -rf /root/.cache/pip*

# Fase7b: coleta estáticos no build (gunicorn não serve; STATIC_ROOT vai p/ whitenoise/nginx).
# Roda com defaults do settings (sem settings_local/DB) — collectstatic não precisa de banco.
RUN python3 ${NES_DIR}/patientregistrationsystem/qdc/manage.py collectstatic --noinput -v1

VOLUME $NES_DIR

COPY docker/compose/nes/entrypoint.sh /

ENV NES_IP ${NES_IP:-0.0.0.0}
ENV NES_PORT ${NES_PORT:-8000}

ENTRYPOINT [ "/entrypoint.sh" ]

# Fase6: gunicorn em vez de runserver (produção). 3 workers, timeout folgado p/ exports.
CMD [ "/bin/sh", "-c", "python3 -m gunicorn qdc.wsgi:application --bind $NES_IP:$NES_PORT --workers 3 --timeout 120 --chdir ${NES_DIR}/patientregistrationsystem/qdc" ]
