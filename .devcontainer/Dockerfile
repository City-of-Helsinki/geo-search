FROM python:3.12.13-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.12.5@sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1 \
    /uv /uvx /usr/local/bin/

ENV DEBIAN_FRONTEND=noninteractive \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PRE_COMMIT_HOME=/opt/pre-commit-cache \
    PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GIT_CONFIG_GLOBAL=/home/dev/.gitconfig-safe \
    GIT_CONFIG_NOSYSTEM=1 \
    GIT_TERMINAL_PROMPT=0 \
    GIT_SSH_COMMAND=/bin/false

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        ca-certificates \
        curl \
        gdal-bin \
        git \
        libgdal-dev \
        libgeos-dev \
        libpq-dev \
        netcat-openbsd \
        postgresql-client \
        unzip \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 dev \
    && useradd --uid 1000 --gid dev --create-home --shell /bin/bash dev \
    && printf '[credential]\n\thelper =\n' > /home/dev/.gitconfig-safe \
    && chown dev:dev /home/dev/.gitconfig-safe

WORKDIR /tmp/project
COPY pyproject.toml uv.lock .pre-commit-config.yaml ./

RUN uv sync --frozen --group dev \
    && git init --quiet \
    && pre-commit install-hooks \
    && chown -R dev:dev /opt/venv /opt/pre-commit-cache

COPY .devcontainer/dev-entrypoint.sh /usr/local/bin/dev-entrypoint
COPY .devcontainer/run-populate.sh /usr/local/bin/run-populate

RUN chmod 0755 /usr/local/bin/dev-entrypoint /usr/local/bin/run-populate

WORKDIR /workspace
USER dev
ENTRYPOINT ["/usr/local/bin/dev-entrypoint"]
