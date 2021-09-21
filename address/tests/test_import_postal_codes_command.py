from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management import call_command
from pytest import mark

from .factories import AddressFactory


@mark.django_db
def test_import_postal_codes_updates_postal_codes_from_shapefile(paavo_shapefile):
    address = AddressFactory(
        location=Point(x=24.9428, y=60.1666, srid=settings.PROJECTION_SRID),
        postal_code="",
    )
    call_command("import_postal_codes", [paavo_shapefile])
    address.refresh_from_db()
    assert address.postal_code == "00100"
