#!/bin/sh

set -eu

if ! grep -qx '# Host .env is intentionally masked inside development containers.' /workspace/.env
then
    echo "Refusing to start: /workspace/.env is not the expected credential mask." >&2
    exit 1
fi

for env_file in /workspace/.env.*
do
    [ -e "$env_file" ] || continue
    [ "$env_file" = /workspace/.env.example ] && continue
    echo "Refusing to start: $env_file would expose host credentials." >&2
    echo "Move it outside the project before starting the development container." >&2
    exit 1
done

if [ -n "${DATABASE_HOST:-}" ]; then
    until nc -z -w 2 "$DATABASE_HOST" 5432; do
        echo "Waiting for PostgreSQL at ${DATABASE_HOST}:5432..."
        sleep 1
    done
fi

if [ "${APPLY_MIGRATIONS:-0}" = "1" ]; then
    python manage.py migrate --noinput
fi

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec python manage.py runserver 0.0.0.0:8080
