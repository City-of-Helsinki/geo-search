from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from address import urls as addresses_urls
from address.api.wfs_views import GeoWFSView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include((addresses_urls, "address"), namespace="v1/address")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="schema-docs",
    ),
    path("wfs/geo/", GeoWFSView.as_view()),
]


urlpatterns += [path("", include("helsinki_health_endpoints.urls"))]

if settings.DEBUG and settings.DEBUG_TOOLBAR:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
