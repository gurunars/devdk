FROM python:3.6-alpine

ENV JAVA_HOME=/usr/lib/jvm/default-jvm
ENV LANG en_US.UTF-8

RUN apk update && \
    apk add --no-cache python3-dev gcc musl-dev linux-headers zeromq-dev shadow && \
    pip install -U pip jupyter && \
    mkdir /var/mail && \
    mkdir project && \
    ln -s /usr/local/bin/pip /usr/sbin/pip

ADD /config.py /
ADD /start.sh /

WORKDIR /project

ENTRYPOINT ["/start.sh"]
