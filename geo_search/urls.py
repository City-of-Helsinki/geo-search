from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.decorators.http import require_GET
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from address import urls as addresses_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include((addresses_urls, "address"), namespace="v1/address")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="schema-docs",
    ),
]


@require_GET
def healthz(*args, **kwargs) -> HttpResponse:
    """Returns status code 200 if the server is alive."""
    return HttpResponse(status=200)


@require_GET
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
