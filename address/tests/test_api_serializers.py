from pytest import mark

from ..api.serializers import (
    AddressSerializer,
    MunicipalitySerializer,
    StreetSerializer,
)
from ..tests.factories import AddressFactory, MunicipalityFactory, StreetFactory


@mark.django_db
def test_municipality_serializer():
    municipality = MunicipalityFactory()
    serializer = MunicipalitySerializer()
    actual = serializer.to_representation(municipality)
    assert actual == {
        "name": {
            "fi": municipality.get_translation("fi", "translations").name,
            "sv": municipality.get_translation("sv", "translations").name,
        }
    }


@mark.django_db
def test_street_serializer():
    street = StreetFactory()
    serializer = StreetSerializer()
    actual = serializer.to_representation(street)
    assert actual == {
        "municipality": {
            "name": {
                "fi": street.municipality.get_translation("fi", "translations").name,
                "sv": street.municipality.get_translation("sv", "translations").name,
            }
        },
        "name": {
            "fi": street.get_translation("fi", "translations").name,
            "sv": street.get_translation("sv", "translations").name,
        },
    }


@mark.django_db
def test_address_serializer():
    address = AddressFactory()
    serializer = AddressSerializer()
    actual = serializer.to_representation(address)
    street = address.street
    municipality = street.municipality
    assert actual == {
        "street": {
            "municipality": {
                "name": {
                    "fi": municipality.get_translation("fi", "translations").name,
                    "sv": municipality.get_translation("sv", "translations").name,
                }
            },
            "name": {
                "fi": street.get_translation("fi", "translations").name,
                "sv": street.get_translation("sv", "translations").name,
            },
        },
        "number": address.number,
        "number_end": address.number_end,
        "letter": address.letter,
        "postal_code": address.postal_code,
        "post_office": address.post_office,
        "location": {
            "type": "point",
            "coordinates": [address.location.x, address.location.y],
        },
        "modified_at": address.modified_at.astimezone().isoformat(),
    }
