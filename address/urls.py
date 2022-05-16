from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.views import AddressViewSet, PostalCodeAreaViewSet

router = DefaultRouter()
router.register(r"address", AddressViewSet)
router.register(r"postal_code_area", PostalCodeAreaViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
