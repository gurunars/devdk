FROM python:3.6-alpine

RUN apk update && \
    apk add coreutils sudo && \
    pip install -U pip setuptools

ADD /requirements.txt /build/
RUN pip install -r /build/requirements.txt
ADD / /build/
RUN pip install -U /build 1> /dev/null

WORKDIR /project

ENTRYPOINT ["entry-point"]

ONBUILD ADD /requirements.txt /project/
ONBUILD RUN pip install -r /project/requirements.txt
