from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.views import AddressViewSet, MunicipalityViewSet, PostalCodeAreaViewSet

router = DefaultRouter()
router.register(r"address", AddressViewSet)
router.register(r"postal_code_area", PostalCodeAreaViewSet)
router.register(r"municipality", MunicipalityViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
