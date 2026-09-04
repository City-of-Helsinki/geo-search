#!/bin/sh

set -eu

if ! grep -qx '# Host .env is intentionally masked inside development containers.' /workspace/.env
then
    echo "Refusing to populate: /workspace/.env is not the expected credential mask." >&2
    exit 1
fi

for env_file in /workspace/.env.*
do
    [ -e "$env_file" ] || continue
    [ "$env_file" = /workspace/.env.example ] && continue
    echo "Refusing to populate: $env_file would expose host credentials." >&2
    exit 1
done

usage() {
    cat <<'EOF'
Usage: run-populate <dataset> [arguments]

Datasets:
  municipalities <path-under-project-root>
  digiroad <uusimaa|varsinais-suomi>
  paavo <uusimaa|varsinais-suomi>
  post-office
EOF
}

dataset=${1:-}
if [ -z "$dataset" ] || [ "$dataset" = "--help" ]; then
    usage
    exit 0
fi
shift

case "$dataset" in
    municipalities)
        script=/workspace/scripts/import-municipalities-data.sh
        ;;
    digiroad)
        script=/workspace/scripts/import-digiroad-data.sh
        ;;
    paavo)
        script=/workspace/scripts/import-paavo-data.sh
        ;;
    post-office)
        script=/workspace/scripts/import-post-office-data.sh
        ;;
    *)
        echo "Unknown dataset: $dataset" >&2
        usage >&2
        exit 2
        ;;
esac

: "${DATABASE_URL:?DATABASE_URL must be set}"

home=$(mktemp -d /tmp/populate-home.XXXXXX)
trap 'rm -rf "$home"' EXIT

env -i \
    DATABASE_URL="$DATABASE_URL" \
    HOME="$home" \
    LANG=C.UTF-8 \
    PATH=/opt/venv/bin:/usr/local/bin:/usr/bin:/bin \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TMPDIR=/tmp \
    /bin/sh "$script" "$@"
