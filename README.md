![CI](https://github.com/City-of-Helsinki/geo-search/actions/workflows/ci.yml/badge.svg)
[![SonarCloud Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=City-of-Helsinki_geo-search&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=City-of-Helsinki_geo-search)

# Geo Search

Service for searching geospatial information

## Development with Dev Containers

Prerequisites:

* Docker with Compose support
* Visual Studio Code with the Dev Containers extension

The Dev Container reuses the root Dockerfile's `development` target and
`compose.yaml`. The `overrideCommand` setting in `devcontainer.json` keeps
the Django container running while you start the server and run commands
from the editor terminal.

Open the repository in Visual Studio Code and run **Dev Containers: Reopen in
Container**. After setup finishes, open new terminal and run in the container terminal:

    uv run manage.py migrate
    uv run manage.py runserver 0.0.0.0:8080

The API is available at [localhost:8080/v1](http://localhost:8080/v1). The port is
bound to `127.0.0.1` only. PostgreSQL is not published to the host.

The repository is mounted at `/app`, including any local `.env` file, which
Django reads. The setup permits the editor's normal Git credential integration.

### Rebuilding an existing Dev Container

After changing branches or updating the container configuration, use
**Dev Containers: Rebuild Container** in VS Code. Reopening an existing
container can reuse its previous image, mounts, and startup command.

If startup still fails with an old configuration, close the remote window
and run `docker compose down` from the repository root on the host, then
reopen the repository in a Dev Container. This removes the old containers
but preserves the database volume. Do not add `--volumes` when keeping data.

### Dev Containers CLI

The same environment can be started without Visual Studio Code by using the
[Dev Containers CLI](https://github.com/devcontainers/cli). Install the CLI
(e.g. `npm install --global @devcontainers/cli`, then run this command from
the repository root:

    devcontainer up

This uses the same `.devcontainer/devcontainer.json` as VS Code. Start the
application with:

    devcontainer exec uv run manage.py migrate
    devcontainer exec uv run manage.py runserver 0.0.0.0:8080

Run other commands in another host terminal with `devcontainer exec`:

    devcontainer exec uv run manage.py check
    devcontainer exec uv run pytest
    devcontainer exec uv run ruff check

Stop the environment from the repository root with:

    docker compose down

This stops the containers and preserves the database volume.

To intentionally remove the database and initialize a new empty one,
use command:

    docker compose down --volumes

Python dependencies are installed in the image. Dev Container setup installs
the pre-commit hooks and their environments. In a container terminal, run:

    ruff check
    ruff format --check
    pre-commit run --all-files
    pytest

### GitHub Copilot CLI

Copilot CLI is optional. Its Dev Container Feature requires Debian/Ubuntu,
so the shared UBI image uses GitHub's [standalone installer](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli)
instead. Run in a container terminal to install the pinned version:

    curl -fsSL https://gh.io/copilot-install -o /tmp/copilot-install.sh
    VERSION=1.0.80 PREFIX=/opt/app-root bash /tmp/copilot-install.sh

The Dev Container has normal outbound network access. Authenticate inside it
with the OAuth device flow and start Copilot:

    copilot login
    copilot

The installation and login are stored in the container and are removed when
it is rebuilt.

## Development with Docker Compose

To start Django automatically without an editor or the Dev Containers CLI:

    docker compose up --build

This starts PostGIS, applies migrations, and runs Django at
[localhost:8080](http://localhost:8080). Run development commands with
`docker compose exec django`, for example:

    docker compose exec django pytest

Use `docker compose down` to stop the environment and preserve its database.
Close and stop an existing Dev Container before switching to this workflow.

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

The project includes shell scripts for importing geospatial data from various
sources. Run the commands below from a Dev Container terminal after applying
migrations. For plain Docker Compose, prefix each command with
`docker compose exec django`. They also work in an activated local Python
environment with the required system tools installed.

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
   from the container terminal:

        ./scripts/import-municipalities-data.sh .devdata/nls/SuomenKuntajako_2026_10k.shp

#### 2. Import addresses and other data

After municipalities are imported, import other data:

    # Import addresses (required, specify province)
    ./scripts/import-digiroad-data.sh uusimaa

The Digiroad download sets a session cookie during redirects. The script
uses a temporary cookie jar so curl can follow them to the ZIP file. The
jar holds no credentials and is deleted when the script exits.

    # Import postal code areas (optional, specify province)
    ./scripts/import-paavo-data.sh uusimaa

    # Import post office names (optional, downloads latest data)
    ./scripts/import-post-office-data.sh

Available provinces: `uusimaa` and `varsinais-suomi`

### Re-importing data

To re-import data (e.g., after updates), run from the container terminal:

    # Delete existing address data inside the Dev Container (prompts for confirmation)
    ./scripts/delete-address-data.sh

    # Re-import municipalities if needed
    ./scripts/import-municipalities-data.sh .devdata/nls/SuomenKuntajako_2026_10k.shp

    # Re-import other data
    ./scripts/import-digiroad-data.sh uusimaa
    ./scripts/import-paavo-data.sh uusimaa
    ./scripts/import-post-office-data.sh

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
