FROM ubuntu:20.04

# Fixes git vulnerability issue in openshift
COPY .gitconfig .
# Fixes git vulnerability issue locally
COPY .gitconfig /etc/gitconfig

WORKDIR /app

RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update && \
    TZ="Europe/Helsinki" DEBIAN_FRONTEND=noninteractive apt-get install -y apt-transport-https python3-pip gdal-bin uwsgi uwsgi-plugin-python3 libgdal26 git-core postgresql-client netcat gettext libpq-dev unzip && \
    ln -s /usr/bin/pip3 /usr/local/bin/pip && \
    ln -s /usr/bin/python3 /usr/local/bin/python

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV STATIC_ROOT /srv/app/static
RUN mkdir -p /srv/app/static

RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic --noinput
RUN python manage.py compilemessages

# Openshift starts the container process with group zero and random ID
# we mimic that here with nobody and group zero
USER nobody:0

ENTRYPOINT ["./docker-entrypoint.sh"]
