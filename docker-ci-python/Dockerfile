FROM python:3.6-alpine

ENV JAVA_HOME=/usr/lib/jvm/default-jvm
ENV LANG en_US.UTF-8

RUN apk update && \
    apk add --no-cache coreutils sudo graphviz ttf-droid ttf-droid-nonlatin openjdk7-jre-base python3-dev && \
    pip install -U pip setuptools && \
    ln -sf "${JAVA_HOME}/bin/"* "/usr/bin/" && \
    cd /usr/share && \
    wget http://vorboss.dl.sourceforge.net/project/plantuml/plantuml.jar && \
    apk del wget

ADD /requirements.txt /build/
RUN pip install -r /build/requirements.txt
ADD / /build/
ADD / /project/

WORKDIR /project

RUN cp /build/configs/setup.py /project/ && \
    pip install -U . 1> /dev/null

RUN entry-point static-checks && \
    entry-point tests

ENTRYPOINT ["entry-point"]

ONBUILD COPY setup.* /requirements*.txt /project/
ONBUILD RUN sh /build/docker/install-if-exists.sh requirements-dev.txt
ONBUILD RUN sh /build/docker/install-if-exists.sh requirements.txt
