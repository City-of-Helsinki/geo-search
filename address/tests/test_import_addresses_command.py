from django.core.management import call_command
from pytest import mark

from address.models import Address, Municipality, Street


@mark.django_db
def test_import_addresses_creates_addresses_from_shapefile(shapefile):
    call_command("import_addresses", [shapefile])
    assert Municipality.objects.count() == 1
    assert Street.objects.count() == 7
    assert Address.objects.count() == 37
