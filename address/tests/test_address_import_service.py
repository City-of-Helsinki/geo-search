from django.conf import settings
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.geos import LineString
from pytest import approx, mark
from typing import Any, Dict
from unittest.mock import MagicMock, Mock

from ..models import Address, Municipality, Street
from ..services.address_import import delete_address_data, import_addresses
from ..tests.factories import AddressFactory, MunicipalityFactory, StreetFactory

TEST_FEATURE_FIELDS = {
    "KUNTAKOODI": 91,
    "TIENIMI_SU": "Testikatu",
    "TIENIMI_RU": "Testgatan",
    "ENS_TALO_O": 1,
    "ENS_TALO_V": 2,
    "VIIM_TAL_O": 3,
    "VIIM_TAL_V": 4,
}

TEST_GEOMETRY = LineString(
    (386000, 6678000, 24),
    (386000, 6678050, 24),
    (386000, 6678100, 24),
    srid=3067,
)


@mark.django_db(transaction=True)
def test_delete_address_data_removes_municipalities_streets_and_addresses():
    MunicipalityFactory()
    StreetFactory()
    AddressFactory()
    delete_address_data()
    assert not Municipality.objects.exists()
    assert not Street.objects.exists()
    assert not Address.objects.exists()


@mark.django_db
def test_import_addresses_does_nothing_if_street_name_is_missing():
    feature = _mock_feature(
        {
            **TEST_FEATURE_FIELDS,
            "TIENIMI_SU": None,
            "TIENIMI_RU": None,
        }
    )
    import_addresses([feature])
    assert not Address.objects.exists()


@mark.django_db
def test_import_addresses_does_nothing_if_street_number_is_missing():
    feature = _mock_feature(
        {
            **TEST_FEATURE_FIELDS,
            "ENS_TALO_O": None,
            "ENS_TALO_V": None,
            "VIIM_TAL_O": None,
            "VIIM_TAL_V": None,
        }
    )
    import_addresses([feature])
    assert not Address.objects.exists()


@mark.django_db
def test_import_addresses_creates_municipalities():
    feature = _mock_feature({**TEST_FEATURE_FIELDS, "KUNTAKOODI": 49})
    import_addresses([feature])
    assert Municipality.objects.translated(name="Espoo").count() == 1


@mark.django_db
def test_import_addresses_creates_streets():
    feature = _mock_feature(
        {**TEST_FEATURE_FIELDS, "KUNTAKOODI": 149, "TIENIMI_SU": "CreationTest"}
    )
    import_addresses([feature])
    assert Street.objects.translated(name="CreationTest").count() == 1


@mark.django_db
def test_import_addresses_creates_addresses():
    feature = _mock_feature({**TEST_FEATURE_FIELDS, "KUNTAKOODI": 186})
    import_addresses([feature])
    street = Street.objects.get()
    expected_locations = [
        (24.94235, 60.22301),  # number 1, left side
        (24.94181, 60.22300),  # number 2, right side
        (24.94232, 60.22346),  # number 3, left side
        (24.94178, 60.22345),  # number 4, right side
    ]
    for number in [1, 2, 3, 4]:
        address = Address.objects.get(number=number, street=street)
        assert address.street.municipality.name == "Järvenpää"
        assert address.location.coords == approx(expected_locations[number - 1])
        assert address.location.srid == settings.PROJECTION_SRID


def _mock_feature(fields: Dict[str, Any]) -> Feature:
    """Create a mock Feature with the test fields and geometry."""
    items = {}
    for key, value in fields.items():
        items[key] = Mock(value=value)
    feature = MagicMock(
        spec=Feature,
        geom=Mock(geos=TEST_GEOMETRY),
    )
    feature.__getitem__.side_effect = lambda k: items[k]
    return feature
