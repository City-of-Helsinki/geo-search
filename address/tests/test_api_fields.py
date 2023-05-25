from django.conf import settings
from django.contrib.gis.geos import Point

from ..api.fields import LocationField


def test_location_field_to_internal_value():
    value = {"type": "Point", "coordinates": [25.07142, 60.41270]}
    expected = Point(*value["coordinates"], srid=settings.PROJECTION_SRID)
    actual = LocationField(initial=expected).to_internal_value(value)
    assert actual.coords == expected.coords
    assert actual.srid == expected.srid


def test_location_field_to_representation():
    coords = [25.07081, 60.41292]
    value = Point(*coords, srid=settings.PROJECTION_SRID)
    expected = {"type": "Point", "coordinates": coords}
    actual = LocationField(initial=expected).to_representation(value)
    assert actual == expected
