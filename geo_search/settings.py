import sentry_sdk
import subprocess
from django.utils.translation import gettext_lazy as _
from environ import Env
from pathlib import Path
from sentry_sdk.integrations.django import DjangoIntegration

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
    SENTRY_DSN=(str, ""),
    SENTRY_ENVIRONMENT=(str, ""),
    REQUIRE_AUTHORIZATION=(bool, True),
)

env_path = BASE_DIR / ".env"
if env_path.exists():
    Env.read_env(env_path)

DEBUG = env.bool("DEBUG")
SECRET_KEY = env.str("SECRET_KEY")
if DEBUG and not SECRET_KEY:
    SECRET_KEY = "secret-for-debugging-only"
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

try:
    version = str(
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
    )
except OSError:
    version = "n/a"

sentry_sdk.init(
    dsn=env.str("SENTRY_DSN"),
    release=version,
    environment=env("SENTRY_ENVIRONMENT"),
    integrations=[DjangoIntegration()],
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
    "corsheaders",
    "rest_framework",
    "rest_framework_api_key",
    "parler",
    "drf_spectacular",
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

# Internationalization
LANGUAGE_CODE = "fi"
LANGUAGES = (("fi", _("Finnish")), ("en", _("English")), ("sv", _("Swedish")))
TIME_ZONE = "Europe/Helsinki"
USE_I18N = True
USE_L10N = True
USE_TZ = True
PARLER_LANGUAGES = {None: ({"code": "fi"}, {"code": "sv"}, {"code": "en"})}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = env.str("STATIC_ROOT")
STATIC_URL = env.str("STATIC_URL")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

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
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Geospatial Search API",
    "DESCRIPTION": "Service for searching geospatial information.",
    "SERVE_INCLUDE_SCHEMA": False,
    "VERSION": None,
}

REQUIRE_AUTHORIZATION = env.bool("REQUIRE_AUTHORIZATION")
