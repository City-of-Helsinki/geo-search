# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1] - 2024-09-24

### What's Changed
* Fix postal code import test by @mhieta in ([94bdc97](https://github.com/City-of-Helsinki/geo-search/commit/94bdc973c8aafaf9859e08fb4453e722027be953))

## [1.1.0] - 2024-09-24

### What's Changed
* Fix Digiroad importer by @japauliina in https://github.com/City-of-Helsinki/geo-search/pull/59
* Add Municipality and PostalCodeArea to WFS feature types by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/60
* Use Ubuntu 22.04 base image with python3-gdal -package by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/61
* Fix address import by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/62
* Add municipality to PostalCodeArea by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/63
* Move Api-Key to custom header by @japauliina in https://github.com/City-of-Helsinki/geo-search/pull/64
* chore: add initial release-please configuration by @japauliina in https://github.com/City-of-Helsinki/geo-search/pull/66
* Fix azure-pipelines by excluding release-please files by @japauliina in https://github.com/City-of-Helsinki/geo-search/pull/67
* Add contact etc. details to OpenAPI documentation by @japauliina in https://github.com/City-of-Helsinki/geo-search/pull/68

### New Contributors
* @japauliina made their first contribution in https://github.com/City-of-Helsinki/geo-search/pull/59

**Full Changelog**: https://github.com/City-of-Helsinki/geo-search/compare/v1.0.0...v.1.1.0

## [1.0.0] - 2023-08-23

### What's Changed
* Add basic Django project by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/1
* Add address app and models by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/2
* Create a superuser if environment variable is set by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/3
* Add finnish translation-files by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/4
* Digiroad address import by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/5
* REST API for addresses by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/6
* Filter by bounding box by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/7
* Add filtering by location by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/8
* Add postal code import by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/9
* Add missing post office field by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/10
* Add ability to get responses in XML format by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/11
* Address performance fixes by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/12
* Add health check and readiness endpoints by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/13
* Fix Python 3.8 incompatibilities and missing 'unzip' by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/14
* Project pipeline yaml files by @Vitals9367 in https://github.com/City-of-Helsinki/geo-search/pull/15
* Fix pytest not working inside Docker container by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/17
* Move pytest dependency back to development requirements by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/18
* Read .env file only if it exists by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/19
* Add ability to filter by post office by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/20
* Add OpenAPI schema and documentation by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/21
* Increase page size from 20 to 100 by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/22
* Fix flaky address serializer test by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/23
* Add GHA-workflows for Continuous Integration and SonarCloud by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/24
* Add request authorization with API keys by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/25
* Configure Sentry by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/26
* Add ability to disable API key / authorization checks by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/27
* Fix tests failing without authorization requirement by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/28
* Update azure-pipelines-stageprod.yml by @Vitals9367 in https://github.com/City-of-Helsinki/geo-search/pull/29
* Use "X-Forwarded-Host" header by @jmp in https://github.com/City-of-Helsinki/geo-search/pull/30
* Feature/import addresses for province of southwest finland by @juuso-j in https://github.com/City-of-Helsinki/geo-search/pull/31
* Support for Postal Code Areas by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/32
* Change imports to use shell scripts by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/33
* Remove duplicate and fix faulty municipality name by @juuso-j in https://github.com/City-of-Helsinki/geo-search/pull/34
* Postal Code Areas Municipality-support by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/35
* Update azure-pipelines-devtest.yml by @lorand-ibm in https://github.com/City-of-Helsinki/geo-search/pull/36
* Update azure-pipelines-stageprod.yml by @lorand-ibm in https://github.com/City-of-Helsinki/geo-search/pull/37
* Git vulnerability issue fix. by @Vitals9367 in https://github.com/City-of-Helsinki/geo-search/pull/38
* [Snyk] Security upgrade certifi from 2023.5.7 to 2023.7.22 by @mhieta in https://github.com/City-of-Helsinki/geo-search/pull/56


**Full Changelog**: https://github.com/City-of-Helsinki/geo-search/commits/v1.0.0
