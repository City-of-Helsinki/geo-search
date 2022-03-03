from django.conf import settings
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.geos import Point, Polygon
from pytest import mark
from typing import Any, Dict
from unittest.mock import MagicMock, Mock

from ..services.postal_code_import import PostalCodeImporter
from ..tests.factories import AddressFactory

TEST_GEOMETRY = Polygon.from_bbox([24.9427, 60.1665, 24.9430, 60.1667])
TEST_GEOMETRY.srid = settings.PROJECTION_SRID


@mark.django_db
def test_import_postal_codes():
    address = AddressFactory(
        location=Point(x=24.9428, y=60.1666, srid=settings.PROJECTION_SRID),
        postal_code="",
        post_office="",
    )
    postal_code = "00100"
    post_office = "Helsinki Keskusta - Etu-Töölö"
    feature = _mock_feature({"posti_alue": postal_code, "nimi": post_office})
    PostalCodeImporter().import_postal_codes([feature])
    address.refresh_from_db()
    assert address.postal_code == postal_code
    assert address.post_office == post_office


@mark.django_db
def test_import_postal_codes_does_not_update_postal_code_if_outside(paavo_shapefile):
    address = AddressFactory(
        # Not within the 00100 postal code area
        location=Point(x=27, y=61, srid=settings.PROJECTION_SRID),
        postal_code="",
        post_office="",
    )
    feature = _mock_feature({"posti_alue": "00100", "nimi": "Helsinki"})
    PostalCodeImporter().import_postal_codes([feature])
    address.refresh_from_db()
    assert not address.postal_code
    assert not address.post_office


def _mock_feature(fields: Dict[str, Any]) -> Feature:
    """Create a mock Feature with the test fields and geometry."""
    items = {}
    for key, value in fields.items():
        items[key] = Mock(value=value)
    feature = MagicMock(spec=Feature, geom=Mock(geos=TEST_GEOMETRY))
    feature.__getitem__.side_effect = lambda k: items[k]
    return feature
