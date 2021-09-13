from django.contrib.gis.geos import Point
from factory.faker import Faker as FactoryBoyFaker
from faker import Faker
from faker.providers import BaseProvider


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
