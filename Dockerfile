# ==============================
FROM helsinki.azurecr.io/ubi9/python-312-gdal AS appbase
# ==============================

# Commit used to pull python-uwsgi-common.
ARG UWSGI_COMMON_REF=1a9d30d172c2c1ca00d5025a4464e98e00565c44

COPY --from=ghcr.io/astral-sh/uv:0.12.5@sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1 /uv /uvx /usr/local/bin/

# Fixes git vulnerability issue in openshift
COPY .gitconfig .
# Fixes git vulnerability issue locally
COPY .gitconfig /etc/gitconfig

ENV STATIC_ROOT=/srv/app/static
ENV TZ="Europe/Helsinki"
# Default for URL prefix, handled by uwsgi, ignored by devserver
# Works like this: "/example" -> http://hostname.domain.name/example
ENV DJANGO_URL_PREFIX=/
ENV UV_PROJECT_ENVIRONMENT=/opt/app-root \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never
ENV PATH="/opt/app-root/bin:$PATH"

WORKDIR /app
USER root

COPY pyproject.toml uv.lock ./

RUN dnf update -y && dnf install -y \
    nmap-ncat \
    postgresql \
    && uv sync --frozen --no-dev --group prod \
    && uv run uwsgi --build-plugin https://github.com/City-of-Helsinki/uwsgi-sentry \
    && mkdir -p /srv/app/static \
    && dnf clean all

# Build and copy the shared uWSGI configuration and logging plugin.
ADD --checksum=sha256:accdf4f78840cd5b6081c3a9636e596a75e39101c937440840209f4cab798625 https://github.com/City-of-Helsinki/python-uwsgi-common/archive/${UWSGI_COMMON_REF}.tar.gz /usr/src/python-uwsgi-common.tar.gz
RUN mkdir -p /usr/src/python-uwsgi-common && \
    tar --strip-components=1 -xzf /usr/src/python-uwsgi-common.tar.gz -C /usr/src/python-uwsgi-common && \
    mkdir -p /etc/uwsgi && \
    cp /usr/src/python-uwsgi-common/uwsgi-base.ini /etc/uwsgi/uwsgi-base.ini && \
    uv run uwsgi --build-plugin /usr/src/python-uwsgi-common && \
    rm -rf /usr/src/python-uwsgi-common.tar.gz /usr/src/python-uwsgi-common

ENTRYPOINT ["./docker-entrypoint.sh"]
EXPOSE 8080/tcp

# ==============================
FROM appbase AS development
# ==============================

ENV DEV_SERVER=1

RUN uv sync --frozen --group dev --group prod

COPY . .

USER default

# ==============================
FROM appbase AS production
# ==============================
COPY . .

RUN DJANGO_SECRET_KEY="only-used-for-collectstatic" DATABASE_URL="sqlite:///" \
    python manage.py collectstatic --noinput && \
    python manage.py compilemessages

USER default
