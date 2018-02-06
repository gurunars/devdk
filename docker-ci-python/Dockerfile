FROM python:3.6-alpine

ENV JAVA_HOME=/usr/lib/jvm/default-jvm

RUN apk update && \
    apk add --no-cache coreutils sudo graphviz openjdk7 python3-dev && \
    pip install -U pip setuptools && \
    ln -sf "${JAVA_HOME}/bin/"* "/usr/bin/" && \
    cd /usr/share && \
    wget http://vorboss.dl.sourceforge.net/project/plantuml/plantuml.jar && \
    apk del wget

ADD /requirements.txt /build/
RUN pip install -r /build/requirements.txt
ADD / /build/
RUN pip install -U /build 1> /dev/null

WORKDIR /project

ENTRYPOINT ["entry-point"]

ONBUILD ADD /requirements.txt /project/
ONBUILD RUN pip install -r /project/requirements.txt
