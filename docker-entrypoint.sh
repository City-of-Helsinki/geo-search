#!/bin/bash

set -e

# Wait for the database to be available
if [ -n "$DATABASE_HOST" ]; then
  until nc -z -v -w30 "$DATABASE_HOST" 5432
  do
    echo "Waiting for PostgreSQL database connection..."
    sleep 1
  done
  echo "Database is up!"
fi

# Apply database migrations
if [[ "$APPLY_MIGRATIONS" = "1" ]]; then
    echo "Applying database migrations..."
    ./manage.py migrate --noinput
fi

# Create admin user. Generate password if there isn't one in the
# environment variables.
if [[ "$CREATE_SUPERUSER" = "1" ]]; then
    if [[ "$ADMIN_USER_PASSWORD" ]]; then
        DJANGO_SUPERUSER_PASSWORD=$ADMIN_USER_PASSWORD \
            DJANGO_SUPERUSER_USERNAME=admin \
            DJANGO_SUPERUSER_EMAIL=admin@hel.ninja \
            ./manage.py createsuperuser --noinput || true
    else
        DJANGO_SUPERUSER_PASSWORD=admin \
            DJANGO_SUPERUSER_USERNAME=admin \
            DJANGO_SUPERUSER_EMAIL=admin@hel.ninja \
            ./manage.py createsuperuser --noinput || true
    fi
fi

# Start server
if [[ -n "$*" ]]; then
    "$@"
elif [[ "$DEV_SERVER" = "1" ]]; then
    python ./manage.py runserver 0.0.0.0:8080
else
    uwsgi --ini uwsgi.ini
fi
