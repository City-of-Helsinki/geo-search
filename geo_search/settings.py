import os
from pathlib import Path

import sentry_sdk
from corsheaders.defaults import default_headers
from django.utils.log import DEFAULT_LOGGING
from django.utils.translation import gettext_lazy as _
from environ import Env
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.types import SamplingContext

GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = os.environ.get("GEOS_LIBRARY_PATH")

# Enable logging to console from our modules by configuring the root logger
DEFAULT_LOGGING["loggers"][""] = {
    "handlers": ["console"],
    "level": "INFO",
    "propagate": True,
}

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "temp_key"),
    ALLOWED_HOSTS=(list, []),
    STATIC_ROOT=(str, str(BASE_DIR / "static")),
    STATIC_URL=(str, "/static/"),
    DATABASE_URL=(
        str,
        "postgis://geo-search:geo-search@localhost:5432/geo-search",
    ),
    DATABASE_PASSWORD=(str, ""),
    SENTRY_DSN=(str, ""),
    SENTRY_ENVIRONMENT=(str, "local"),
    SENTRY_PROFILE_SESSION_SAMPLE_RATE=(float, None),
    SENTRY_RELEASE=(str, None),
    SENTRY_TRACES_SAMPLE_RATE=(float, None),
    SENTRY_TRACES_IGNORE_PATHS=(list, ["/healthz", "/readiness"]),
    REQUIRE_AUTHORIZATION=(bool, True),
    DJANGO_LOG_LEVEL=(str, "INFO"),
)

env_path = BASE_DIR / ".env"
if env_path.exists():
    Env.read_env(env_path)

DEBUG = env.bool("DEBUG")
SECRET_KEY = env.str("SECRET_KEY")
if DEBUG and not SECRET_KEY:
    SECRET_KEY = "secret-for-debugging-only"
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

SENTRY_TRACES_SAMPLE_RATE = env("SENTRY_TRACES_SAMPLE_RATE")
SENTRY_TRACES_IGNORE_PATHS = env.list("SENTRY_TRACES_IGNORE_PATHS")


def sentry_traces_sampler(sampling_context: SamplingContext) -> float:
    # Respect parent sampling decision if one exists. Recommended by Sentry.
    if (parent_sampled := sampling_context.get("parent_sampled")) is not None:
        return float(parent_sampled)

    # Exclude health check endpoints from tracing
    path = sampling_context.get("wsgi_environ", {}).get("PATH_INFO", "")
    if path.rstrip("/") in SENTRY_TRACES_IGNORE_PATHS:
        return 0

    # Use configured sample rate for all other requests
    return SENTRY_TRACES_SAMPLE_RATE or 0


if env("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        environment=env("SENTRY_ENVIRONMENT"),
        release=env("SENTRY_RELEASE"),
        integrations=[DjangoIntegration()],
        traces_sampler=sentry_traces_sampler,
        profile_session_sample_rate=env("SENTRY_PROFILE_SESSION_SAMPLE_RATE"),
        profile_lifecycle="trace",
    )

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    "corsheaders",
    "rest_framework",
    "rest_framework_api_key",
    "parler",
    "drf_spectacular",
    "gisserver",
    # Local apps
    "address",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

ROOT_URLCONF = "geo_search.urls"

WSGI_APPLICATION = "geo_search.wsgi.application"

# Databases
DATABASES = {"default": env.db()}

if env("DATABASE_PASSWORD"):
    DATABASES["default"]["PASSWORD"] = env("DATABASE_PASSWORD")

# Internationalization
LANGUAGE_CODE = "fi"
LANGUAGES = (("fi", _("Finnish")), ("en", _("English")), ("sv", _("Swedish")))
TIME_ZONE = "Europe/Helsinki"
USE_I18N = True
USE_TZ = True
PARLER_LANGUAGES = {None: ({"code": "fi"}, {"code": "sv"}, {"code": "en"})}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = env.str("STATIC_ROOT")
STATIC_URL = env.str("STATIC_URL")
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# SRID for the locations stored in the application database
PROJECTION_SRID = 4326  # WGS84

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework_xml.renderers.XMLRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": [
        "geo_search.permissions.IsAuthorized",
    ],
    "DEFAULT_PAGINATION_CLASS": "geo_search.pagination.Pagination",
    "PAGE_SIZE": 100,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Geospatial Search API",
    "DESCRIPTION": "Service for searching geospatial information. "
    "To request an API-Key, email palvelukartta@hel.fi.",
    "SERVE_INCLUDE_SCHEMA": False,
    "VERSION": "v1",
    "CONTACT": {
        "name": "City of Helsinki",
        "url": "https://www.hel.fi",
    },
    "LICENSE": {
        "name": "MIT",
        "url": "https://opensource.org/license/MIT",
    },
    "AUTHENTICATION_WHITELIST": [],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Api-Key",
            }
        }
    },
    "SECURITY": [
        {
            "ApiKeyAuth": [],
        }
    ],
}

REQUIRE_AUTHORIZATION = env.bool("REQUIRE_AUTHORIZATION")
API_KEY_CUSTOM_HEADER = "HTTP_API_KEY"

USE_X_FORWARDED_HOST = True

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = (
    *default_headers,
    "baggage",
    "sentry-trace",
)
