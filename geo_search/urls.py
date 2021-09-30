from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from address import urls as addresses_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include((addresses_urls, "address"), namespace="v1/address")),
]


def healthz(*args, **kwargs) -> HttpResponse:
    """Returns status code 200 if the server is alive."""
    return HttpResponse(status=200)


def readiness(*args, **kwargs) -> HttpResponse:
    """
    Returns status code 200 if the server is ready to perform its duties.

    This goes through each database connection and perform a standard SQL
    query without requiring any particular tables to exist.
    """
    from django.db import connections

    for name in connections:
        cursor = connections[name].cursor()
        cursor.execute("SELECT 1;")
        cursor.fetchone()

    return HttpResponse(status=200)


urlpatterns += [path("healthz", healthz), path("readiness", readiness)]
