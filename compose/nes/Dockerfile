FROM alpine:3.8 as wheeler
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
		libpng-dev \
		freetype-dev \
		build-base \
		git \
		postgresql-dev \
		openblas-dev \
		libjpeg-turbo-dev \
		python3-dev && \
	apk add --no-cache \
		--repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
		hdf5-dev && \
	rm -rf /var/cache/apk/* && \
	ln -s /usr/include/locale.h /usr/include/xlocale.h && \
	git clone -j $(nproc) https://github.com/neuromat/nes.git

RUN mkdir -p /wheels/requirement && \
		cp /nes/patientregistrationsystem/qdc/requirements.txt /wheels/requirement

WORKDIR /wheels

RUN pip3 install -r requirement/requirements.txt && \
		pip3 install -U wheel && \
		pip3 wheel -r requirement/requirements.txt

FROM alpine:3.8

RUN apk update && \
	apk add --no-cache \
	git \
	libpq \
	openblas-dev \
	python3 && \
	apk add --no-cache \
		--repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
		hdf5-dev

ARG NES_TAG=unset
ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR

RUN mkdir -p "$NES_DIR"  && \
	if [ "$NES_TAG" = "unset" ]; then \
		git clone -j $(nproc)  https://github.com/neuromat/nes.git $NES_DIR ;\
	else \
		wget https://github.com/neuromat/nes/archive/TAG-"${NES_TAG}".tar.gz -qO - | \
			tar xzv --strip-components=1 -C "$NES_DIR"; \
	fi

COPY --from=wheeler /wheels /wheels

RUN pip3 install -r /wheels/requirement/requirements.txt -f /wheels && \
		rm -rf /wheels && \
		rm -rf /root/.cache/pip*

VOLUME $NES_DIR

COPY ./entrypoint.sh /

ENV NES_IP ${NES_IP:-0.0.0.0}
ENV NES_PORT ${NES_PORT:-8000}

ENTRYPOINT [ "/entrypoint.sh" ]

CMD [ "/bin/sh", "-c", "/usr/bin/python3 ${NES_DIR}/patientregistrationsystem/qdc/manage.py runserver -v3 $NES_IP:$NES_PORT" ]
#CMD [ "sleep", "24h" ]
