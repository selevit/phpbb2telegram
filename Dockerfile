FROM python:3.6
MAINTAINER Sergey Levitin <selevit@gmail.com>

VOLUME ["/app/.last_message_id"]
CMD ["python", "main.py"]

RUN set -x && \
    export DEBIAN_FRONTEND=noninteractive && \
    sed -i 's|deb.debian.org|mirror.yandex.ru|' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|mirror.yandex.ru/debian-security|' /etc/apt/sources.list && \
    apt-get update -qq && \
    apt-get install --no-install-recommends -y libxml2-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app
COPY requirements.txt /app

RUN set -x && \
    pip install --no-cache-dir --disable-pip-version-check --upgrade pip && \
    pip install --no-cache-dir --disable-pip-version-check --upgrade setuptools && \
    pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY . /app

RUN set -x \
    chmod -R a+rX /app/main && \
    find . -name '__pycache__' -type d | xargs rm -rf && \
    python -c 'import compileall, os; compileall.compile_dir(os.curdir, force=1)'

ARG APP_VERSION
ENV APP_VERSION ${APP_VERSION:-local_commit}
