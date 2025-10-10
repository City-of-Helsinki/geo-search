# ==============================
FROM helsinki.azurecr.io/ubi9/python-312-gdal AS appbase
# ==============================

# Fixes git vulnerability issue in openshift
COPY .gitconfig .
# Fixes git vulnerability issue locally
COPY .gitconfig /etc/gitconfig

ENV STATIC_ROOT=/srv/app/static
ENV TZ="Europe/Helsinki"
# Default for URL prefix, handled by uwsgi, ignored by devserver
# Works like this: "/example" -> http://hostname.domain.name/example
ENV DJANGO_URL_PREFIX=/

WORKDIR /app
USER root

COPY requirements.txt .

RUN dnf update -y && dnf install -y \
    nmap-ncat \
    postgresql \
    && pip install -U pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && uwsgi --build-plugin https://github.com/City-of-Helsinki/uwsgi-sentry \
    && mkdir -p /srv/app/static \
    && dnf clean all

ENTRYPOINT ["./docker-entrypoint.sh"]
EXPOSE 8080/tcp

# ==============================
FROM appbase AS development
# ==============================

ENV DEV_SERVER=1

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

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
