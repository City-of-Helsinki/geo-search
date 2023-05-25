from django.conf import settings
from django.contrib.gis.geos import Point
from rest_framework import serializers


class LocationField(serializers.Field):
    """
    A serializer field that represents a location (a Point instance).
    This uses the projection defined in settings.PROJECTION_SRID.
    """

    def to_internal_value(self, value: dict) -> Point:
        return Point(
            *value["coordinates"],
            srid=settings.PROJECTION_SRID,
        )

    def to_representation(self, value) -> dict:
        return {
            "type": "Point",
            "coordinates": list(value.coords),
        }
