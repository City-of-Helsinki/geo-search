from pathlib import Path

from django.contrib.gis.geos import Point
from factory.faker import Faker as FactoryBoyFaker
from faker import Faker
from faker.providers import BaseProvider
from pytest import fixture
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey


@fixture
def api_client() -> APIClient:
    api_key = APIKey.objects.create_key(name="test")[-1]
    return APIClient(HTTP_API_KEY=api_key)


@fixture
def shapefile() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "shapefile.shp"


@fixture
def paavo_shapefile() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "postalcodes.shp"


class DjangoLocationProvider(BaseProvider):
    """Provides a random location for a PointField."""

    _faker = Faker()

    def location(self, **kwargs):
        coords = self._faker.local_latlng(**kwargs, coords_only=True)
        return Point(
            x=float(coords[1]),
            y=float(coords[0]),
            srid=4326,  # Faker gives the coordinates in WGS84
        )


FactoryBoyFaker.add_provider(DjangoLocationProvider)
