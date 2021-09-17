from django.contrib import admin
from django.urls import include, path

from address import urls as addresses_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include((addresses_urls, "address"), namespace="v1/address")),
]
