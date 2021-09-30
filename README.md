# geo-search

Service for searching geospatial information

## Development with Docker

1. Copy the contents of `.env.example` to `.env` and modify it if needed
2. Run `docker compose up`

The project is now running at [localhost:8081](http://localhost:8081)

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
