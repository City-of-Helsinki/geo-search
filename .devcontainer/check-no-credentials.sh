#!/bin/sh

set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
project_root=$(dirname "$script_dir")

for env_file in "$project_root"/.env.*
do
    [ -e "$env_file" ] || continue
    [ "$env_file" = "$project_root/.env.example" ] && continue
    echo "Dev Container startup blocked: $(basename "$env_file") may contain credentials." >&2
    echo "Move it outside the mounted project root and retry." >&2
    exit 1
done

for relative_path in \
    credentials.json \
    service-account.json \
    .aws \
    .azure \
    .kube \
    .ssh
do
    if [ -e "$project_root/$relative_path" ]; then
        echo "Dev Container startup blocked: $relative_path may contain credentials." >&2
        echo "Move it outside the mounted project root and retry." >&2
        exit 1
    fi
done
