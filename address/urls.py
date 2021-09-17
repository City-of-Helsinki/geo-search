from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.views import AddressViewSet

router = DefaultRouter()
router.register(r"address", AddressViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
