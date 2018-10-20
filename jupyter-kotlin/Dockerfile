FROM python:3.6-alpine

ENV JAVA_HOME=/usr/lib/jvm/default-jvm
ENV LANG en_US.UTF-8

RUN apk update && \
    apk add --no-cache git python3-dev openjdk8 gcc musl-dev linux-headers zeromq-dev bash && \
    pip install -U pip jupyter && \
    git clone https://github.com/ligee/kotlin-jupyter.git && \
    cd /kotlin-jupyter && \
    ./gradlew install && \
    cd / && \
    rm -rf kotlin-jupyter && \
    apk del git bash

RUN apk add shadow && \
    mkdir /var/mail && \
    mkdir project

ADD /start.sh /

WORKDIR /project

ENTRYPOINT ["/start.sh"]