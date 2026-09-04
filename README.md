![CI](https://github.com/City-of-Helsinki/geo-search/actions/workflows/ci.yml/badge.svg)
[![SonarCloud Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=City-of-Helsinki_geo-search&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=City-of-Helsinki_geo-search)

# Geo Search

Service for searching geospatial information

## Development with Dev Containers

Prerequisites:

* Docker with Compose support
* Visual Studio Code with the Dev Containers extension

The development environment intentionally does not mount the Docker socket,
host home directory, SSH agent, cloud configuration, or credential files. All
host bind sources stay inside the project root. A project-owned empty file is
mounted over `/workspace/.env`, so an existing host `.env` remains untouched
but is not visible inside the containers. Other `.env.*` credential files and
recognized credential directories still make startup fail closed.

Open the repository in Visual Studio Code and run **Dev Containers: Reopen in
Container**. Compose starts Django and PostGIS, applies migrations, and VS Code
forwards the API at [localhost:8080](http://localhost:8080). PostgreSQL is not
published to the host.

Dependencies and pre-commit hook environments are installed in the image, so
the standard development commands are immediately available:

    ruff check
    ruff format --check
    pre-commit run --all-files
    pytest

The database uses a persistent named volume and starts without application
data. To remove the database and initialize a new empty one, close the Dev
Container and run from a host terminal:

    docker compose down --volumes

### GitHub Copilot CLI

The Dev Container installs GitHub Copilot CLI with the official Dev Container
Feature. Its version is pinned, and no GitHub token or host credential store is
passed into the container.

The Dev Container has normal outbound network access. Authenticate inside it
with the OAuth device flow and start Copilot:

    copilot login
    copilot

The login is stored only in the container and is removed when the container is
rebuilt.

## Development without Docker

Prerequisites:

* PostgreSQL 17 or higher with PostGIS extension
* Python 3.12 or higher

### Installing Python requirements

First, make sure `uv` is installed. See the [official installer](https://docs.astral.sh/uv/getting-started/installation/) or run:

    pip install uv

Verify with `uv --version`.

* Run `uv sync --group dev`

This creates a virtual environment at `.venv/` and installs all production and development dependencies exactly as pinned in `uv.lock`.

To activate the virtual environment:

    source .venv/bin/activate

The `.venv/` environment is only for local development without Docker. The
container image uses `UV_PROJECT_ENVIRONMENT=/opt/app-root` and adds
`/opt/app-root/bin` to `PATH` in the Dockerfile; it does not use `VIRTUAL_ENV` or
`/opt/venv`.

### Database

To setup a database compatible with default database settings:

Create user and database

    sudo -u postgres createuser -P -R -S geo-search  # use password `geo-search`
    sudo -u postgres createdb -O geo-search geo-search

Allow user to create test database

    sudo -u postgres psql -c 'ALTER USER "geo-search" CREATEDB;'

Create the PostGIS extension if needed

    sudo -u postgres psql -c 'CREATE EXTENSION postgis;'

## Import or re-import data

The project includes convenient shell scripts for importing geospatial
data from various sources.

### Available import scripts

* `scripts/import-municipalities-data.sh` - Import municipalities from NLS (requires manual download)
* `scripts/import-digiroad-data.sh` - Import address data from Digiroad / Finnish Transport Infrastructure Agency
* `scripts/import-paavo-data.sh` - Import postal code areas from Paavo / Statistics Finland
* `scripts/import-post-office-data.sh` - Import post office names from Posti
* `scripts/delete-address-data.sh` - Delete all address data (with confirmation)

### First-time import

**Important:** Municipality data must be imported first, before importing addresses.

#### 1. Import municipalities (required, manual download)

Municipality data must be manually downloaded from NLS:

1. Visit [NLS Administrative Areas](https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/datasets-and-interfaces/product-descriptions/division-administrative-areas-vector)
2. Download the dataset following NLS's download process
3. Extract the ZIP file to a directory (e.g., `/tmp/nls/`)
4. Put the extracted files under the gitignored `.devdata/` directory and run
   the sandboxed population service from a host terminal:

        docker compose --profile populate run --rm populate \
            municipalities .devdata/nls/SuomenKuntajako_2026_10k.shp

#### 2. Import addresses and other data

After municipalities are imported, import other data:

    # Import addresses (required, specify province)
    docker compose --profile populate run --rm populate digiroad uusimaa

The Digiroad download endpoint establishes a session during its redirect
chain. The import script keeps a temporary curl cookie jar for that single
download, passing it on each redirect so the request can reach the ZIP archive
instead of looping until curl's redirect limit. The jar is created under the
system temporary directory and removed on completion, interruption, or error;
it does not contain project credentials and is not persisted in the repository.

    # Import postal code areas (optional, specify province)
    docker compose --profile populate run --rm populate paavo uusimaa

    # Import post office names (optional, downloads latest data)
    docker compose --profile populate run --rm populate post-office

Available provinces: `uusimaa` and `varsinais-suomi`

### Re-importing data

To re-import data (e.g., after updates):

    # Delete existing address data inside the Dev Container (prompts for confirmation)
    ./scripts/delete-address-data.sh

    # Re-import municipalities if needed
    docker compose --profile populate run --rm populate \
        municipalities .devdata/nls/SuomenKuntajako_2026_10k.shp

    # Re-import other data
    docker compose --profile populate run --rm populate digiroad uusimaa
    docker compose --profile populate run --rm populate paavo uusimaa
    docker compose --profile populate run --rm populate post-office

The dedicated population service runs as a non-root user with a read-only
project filesystem, a cleared environment, dropped capabilities,
`no-new-privileges`, and no Docker socket. Only the database URL is passed to
the import script.

### Manual import using Django commands

You can also use the Django management commands directly:

    # Import municipalities (required first, manual download needed)
    python manage.py import_municipalities <path-to-shapefile>

    # Import addresses
    python manage.py import_addresses <path-to-shapefiles> <province>

    # Import postal code areas
    python manage.py import_postal_code_areas <province> <path-to-shapefiles>

    # Import post office names
    python manage.py import_post_offices <path-to-zip-file>
    # or download directly:
    python manage.py import_post_offices --url <url-to-posti-zip>

    # Delete all address data
    python manage.py delete_address_data

## Keeping Python requirements up to date

### Adding and removing dependencies

The following commands automatically update both `pyproject.toml` and `uv.lock` — no need to run `uv lock` separately afterwards:

Outside or inside the Dev Container:

* Add a production dependency: `uv add <package>`
* Add a development dependency: `uv add --group dev <package>`
* Remove a dependency: `uv remove <package>`

### Upgrading packages

To upgrade to the newest versions allowed by `exclude-newer` and version constraints:

* Upgrade a single package: `uv lock --upgrade-package <package>`
* Upgrade all packages: `uv lock --upgrade`

Then apply the updated lock file locally:

    uv sync --group dev

The `uv.lock` file must always be committed to version control — it is the source of truth for reproducible builds.

## Code format

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and quality checking.

Basic `ruff` commands:

* lint: `ruff check`
* apply safe lint fixes: `ruff check --fix`
* check formatting: `ruff format --check`
* format: `ruff format`

[`pre-commit`](https://pre-commit.com/) can be used to install and
run all the formatting tools as git hooks automatically before a
commit.

## Commit message format

New commit messages must adhere to the [Conventional Commits](https://www.conventionalcommits.org/)
specification, and line length is limited to 72 characters.

When [`pre-commit`](https://pre-commit.com/) is in use, [
`commitlint`](https://github.com/conventional-changelog/commitlint)
checks new commit messages for the correct format.

## REST API authorization

To use the REST API, you must be either logged in via the Django
admin interface (for debugging purposes), or an API key must be
provided in the `Authorization` header.

### Generating API keys

A new API key can be created in the Django admin interface under
"API keys". When creating an API key, it will be shown to you only
once, so make sure you copy it.

### Making authorized requests

Clients must pass their API key via header.
It must be formatted as follows:

    Api-Key: <API_KEY>

Where `<API_KEY>` refers to the full generated API key.

### Disabling authorization checks

By default, an API key or an active  session is required to use the API.

To make the API completely public set `REQUIRE_AUTHORIZATION=0` in your
environment variables.
