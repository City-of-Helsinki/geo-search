from pytest import mark

from ..api.serializers import (
    AddressSerializer,
    MunicipalitySerializer,
    PostalCodeAreaSerializer,
    StreetSerializer,
)
from ..tests.factories import (
    AddressFactory,
    MunicipalityFactory,
    PostalCodeAreaFactory,
    StreetFactory,
)


@mark.django_db
def test_municipality_serializer():
    municipality = MunicipalityFactory()
    serializer = MunicipalitySerializer()
    actual = serializer.to_representation(municipality)
    assert actual == {
        "code": municipality.code,
        "name": {t.language_code: t.name for t in municipality.translations.all()},
    }


@mark.django_db
def test_street_serializer():
    street = StreetFactory()
    serializer = StreetSerializer()
    actual = serializer.to_representation(street)
    assert actual == {
        "name": {t.language_code: t.name for t in street.translations.all()},
    }


@mark.django_db
def test_postal_code_area_serializer():
    postal_code_area = PostalCodeAreaFactory()
    serializer = PostalCodeAreaSerializer()
    actual = serializer.to_representation(postal_code_area)
    assert actual == {
        "postal_code": postal_code_area.postal_code,
        "name": {t.language_code: t.name for t in postal_code_area.translations.all()},
    }


@mark.django_db
def test_address_serializer():
    address = AddressFactory()
    serializer = AddressSerializer()
    actual = serializer.to_representation(address)
    street = address.street
    municipality = address.municipality
    assert actual == {
        "street": {
            "name": {t.language_code: t.name for t in street.translations.all()},
        },
        "number": address.number,
        "number_end": address.number_end,
        "letter": address.letter,
        "postal_code_area": {
            "postal_code": address.postal_code_area.postal_code,
            "name": {
                t.language_code: t.name
                for t in address.postal_code_area.translations.all()
            },
        },
        "location": {
            "type": "point",
            "coordinates": [address.location.x, address.location.y],
        },
        "municipality": {
            "code": municipality.code,
            "name": {t.language_code: t.name for t in municipality.translations.all()},
        },
        "modified_at": address.modified_at.astimezone().isoformat(),
    }
