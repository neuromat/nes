FROM python:3.8-alpine3.12 as wheeler
ENV PYTHONUNBUFFERED=1

RUN apk update && \
	apk add --no-cache \
		libpng-dev \
		freetype-dev \
		build-base \
		git \
		postgresql-dev \
		openblas-dev \
		libjpeg-turbo-dev \
		hdf5-dev && \
	rm -rf /var/cache/apk/* && \
	ln -s /usr/include/locale.h /usr/include/xlocale.h

ARG NES_TAG=unset
ARG NES_BRANCH=unset
ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR

RUN mkdir -p "$NES_DIR"  && \
		if [ "$NES_TAG" != "unset" ]; then \
			echo Cloning tag "$NES_TAG" ;\
			wget https://github.com/neuromat/nes/archive/TAG-"${NES_TAG}".tar.gz -qO - | \
				tar xzv --strip-components=1 -C "$NES_DIR" ;\
			sed -i 's/\(psycopg2==\)[0-9.]\+/\12.7.5/' /nes/patientregistrationsystem/qdc/requirements.txt ;\
			sed -i '1isetuptools>=40.6.3' /nes/patientregistrationsystem/qdc/requirements.txt ;\
			sed -i '1ipip>=18.1' /nes/patientregistrationsystem/qdc/requirements.txt ;\
			echo 'mne>=0.17.0' >> /nes/patientregistrationsystem/qdc/requirements.txt ;\
			echo '-e "git+https://github.com/AllenInstitute/nwb-api.git#egg=nwb&subdirectory=ainwb"' >> /nes/patientregistrationsystem/qdc/requirements.txt ;\
		elif [ "$NES_BRANCH" != "unset" ]; then \
			echo Cloning "$NES_BRANCH" branch ;\
			git clone -j $(nproc) -b "$NES_BRANCH"  https://github.com/neuromat/nes.git "$NES_DIR" ;\
		else \
			echo Cloning master branch ;\
			git clone -j $(nproc) https://github.com/neuromat/nes.git "$NES_DIR" ;\
		fi

RUN mkdir -p /wheels/requirement && \
	cp "$NES_DIR"/patientregistrationsystem/qdc/requirements.txt /wheels/requirement

WORKDIR /wheels

RUN pip3 install -U pip setuptools wheel && \
	pip3 install -r requirement/requirements.txt && \
	pip3 wheel -r requirement/requirements.txt

FROM alpine:3.12

SHELL ["/bin/sh","-exc"]

RUN apk update && \
	apk add --no-cache \
		git \
		libpq \
		openblas-dev \
		libjpeg-turbo-dev \
		python3 \
		py3-pip \
		graphviz \
		hdf5-dev && \
	rm -rf /var/cache/apk/*

ARG NES_DIR=/nes
ENV NES_DIR=$NES_DIR

COPY --from=wheeler /wheels /wheels

COPY --from=wheeler $NES_DIR $NES_DIR

RUN pip3 install -U pip setuptools wheel && \
	pip3 install -r /wheels/requirement/requirements.txt -f /wheels && \
		rm -rf /wheels && \
		rm -rf /root/.cache/pip*

VOLUME $NES_DIR

COPY ./entrypoint.sh /

ENV NES_IP ${NES_IP:-0.0.0.0}
ENV NES_PORT ${NES_PORT:-8000}

ENTRYPOINT [ "/entrypoint.sh" ]

CMD [ "/bin/sh", "-c", "/usr/bin/python3 -u ${NES_DIR}/patientregistrationsystem/qdc/manage.py runserver -v3 $NES_IP:$NES_PORT" ]
