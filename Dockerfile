# ==============================
FROM helsinki.azurecr.io/ubi9/python-312-gdal AS appbase
# ==============================

COPY --from=ghcr.io/astral-sh/uv:0.11.24@sha256:99ea34acedc870ba4ad11a1f540a1c04267c9f30aadc465a94406f52dfda2c36 /uv /uvx /usr/local/bin/

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
