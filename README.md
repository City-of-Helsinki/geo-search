![CI](https://github.com/City-of-Helsinki/geo-search/actions/workflows/ci.yml/badge.svg)
[![SonarCloud Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=City-of-Helsinki_geo-search&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=City-of-Helsinki_geo-search)

# Geo Search

Service for searching geospatial information

## Development with Docker

1. Copy the contents of `.env.example` to `.env` and modify it if needed
2. Run `docker compose up`

The project is now running at [localhost:8080](http://localhost:8080)

## Development without Docker

Prerequisites:

* PostgreSQL 11 or higher with PostGIS extension
* Python 3.8 or higher

### Installing Python requirements

* Run `pip install -r requirements.txt`
* Run `pip install -r requirements-dev.txt` (development requirements)

### Database

To setup a database compatible with default database settings:

Create user and database

    sudo -u postgres createuser -P -R -S geo-search  # use password `geo-search`
    sudo -u postgres createdb -O geo-search geo-search

Allow user to create test database

    sudo -u postgres psql -c 'ALTER USER "geo-search" CREATEDB;'

Create the PostGIS extension if needed

    sudo -u postgres psql -c 'CREATE EXTENSION postgis;'

## Keeping Python requirements up to date

1. Add new packages to `requirements.in` or `requirements-dev.in`
2. Update `.txt` file for the changed requirements file:
    * `pip-compile requirements.in`
    * `pip-compile requirements-dev.in`
3. If you want to update dependencies to their newest versions, run:
    * `pip-compile --upgrade requirements.in requirements-dev.in`
4. To install Python requirements run:
    * `pip-sync requirements.txt requirements-dev.txt`

## Code format

This project uses
[`black`](https://github.com/psf/black),
[`flake8`](https://gitlab.com/pycqa/flake8) and
[`isort`](https://github.com/PyCQA/isort)
for code formatting and quality checking. Project follows the basic
black config, without any modifications.

Basic `black` commands:

* To let `black` do its magic: `black .`
* To see which files `black` would change: `black --check .`

## REST API authorization

To use the REST API, you must be either logged in via the Django
admin interface (for debugging purposes), or an API key must be
provided in the `Authorization` header.

### Generating API keys

A new API key can be created in the Django admin interface under
"API keys". When creating an API key, it will be shown to you only
once, so make sure you copy it.

### Making authorized requests

Clients must pass their API key via the `Authorization` header.
It must be formatted as follows:

    Authorization: Api-Key <API_KEY>

Where `<API_KEY>` refers to the full generated API key.

### Disabling authorization checks

By default, an API key or an active  session is required to use the API.

To make the API completely public set `REQUIRE_AUTHORIZATION=0` in your
environment variables.
