FROM python:3.6-alpine

ENV JAVA_HOME=/usr/lib/jvm/default-jvm
ENV LANG en_US.UTF-8

RUN apk update && \
    apk add --no-cache python3-dev openjdk8 gcc musl-dev linux-headers zeromq-dev shadow && \
    pip install -U pip jupyter && \
    mkdir /var/mail && \
    mkdir project

RUN apk add --no-cache git bash && \
    git clone https://github.com/ligee/kotlin-jupyter.git && \
    cd /kotlin-jupyter && \
    ./gradlew install -PinstallPath=/home/jupyter/.ipython/kernels/kotlin && \
    cd / && \
    rm -rf kotlin-jupyter && \
    apk del git bash

ADD /config.py /
ADD /start.sh /

WORKDIR /project

ENTRYPOINT ["/start.sh"]
