FROM public.ecr.aws/ubuntu/ubuntu:22.04

# Fixes git vulnerability issue in openshift
COPY .gitconfig .
# Fixes git vulnerability issue locally
COPY .gitconfig /etc/gitconfig

WORKDIR /app

RUN apt-get update && \
    TZ="Europe/Helsinki" DEBIAN_FRONTEND=noninteractive apt-get install -y apt-transport-https python3-pip gdal-bin uwsgi uwsgi-plugin-python3 postgresql-client netcat gettext git-core libpq-dev unzip tzdata && \
    ln -s /usr/bin/pip3 /usr/local/bin/pip && \
    ln -s /usr/bin/python3 /usr/local/bin/python \
    && apt-get clean

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
