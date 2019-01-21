FROM alpine:3.8

RUN apk update && \
	apk add --no-cache \
	libpng-dev \
	freetype-dev \
	build-base \
	git \
	postgresql-dev \
	openblas-dev \
	libjpeg-turbo-dev \
	python3-dev


RUN ln -s /usr/include/locale.h /usr/include/xlocale.h && \
	echo 'http://linorg.usp.br/AlpineLinux/edge/testing' >> /etc/apk/repositories && \
	apk update && \
	apk add --no-cache hdf5-dev && \
	sed -i '$ d' /etc/apk/repositories

RUN git clone https://github.com/neuromat/nes.git

COPY ./requirements.txt /nes/patientregistrationsystem/qdc

WORKDIR /nes/patientregistrationsystem/qdc 

RUN pip3 install -r requirements.txt

########################################################################################################################################################################################################

COPY ./entrypoint.sh /

ENV NES_IP ${NES_IP:-0.0.0.0}
ENV NES_PORT ${NES_PORT:-8000}

ENTRYPOINT [ "/entrypoint.sh" ]

CMD python3 manage.py runserver $NES_IP:$NES_PORT 2>&1
