#!/bin/sh

set -eu

/bin/sh /workspace/.devcontainer/check-no-credentials.sh

if ! printf '%s\n' '# Host .env is intentionally masked inside development containers.' \
    | cmp -s - /workspace/.env
then
    echo "Refusing to start: /workspace/.env is not the expected credential mask." >&2
    exit 1
fi


if [ "${APPLY_MIGRATIONS:-0}" = "1" ]; then
    python manage.py migrate --noinput
fi

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec python manage.py runserver 0.0.0.0:8080
