from django.urls import reverse
from pytest import mark
from rest_framework.test import APIClient

from ..api.serializers import AddressSerializer
from ..tests.factories import AddressFactory, MunicipalityFactory, StreetFactory


@mark.django_db
def test_get_address_list():
    api_client = APIClient()
    address = AddressFactory()
    serializer = AddressSerializer()
    response = api_client.get(reverse("address:address-list"))
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(address)],
    }


@mark.django_db
def test_filter_addresses_by_street_name():
    api_client = APIClient()
    match = AddressFactory(street=StreetFactory(name="Matching Street"))
    AddressFactory(street=StreetFactory(name="Other Street"))
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"), {"streetname": match.street.name}
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match)],
    }


@mark.django_db
def test_filter_addresses_by_street_number():
    api_client = APIClient()
    matching_number = 42
    matches = [
        AddressFactory(number=matching_number, number_end="99"),
        AddressFactory(number="99", number_end=matching_number),
    ]
    AddressFactory(number="99", number_end="99")
    AddressFactory(number="99", number_end="99")
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"), {"streetnumber": matching_number}
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match) for match in matches],
    }


@mark.django_db
def test_filter_addresses_by_street_letter():
    api_client = APIClient()
    matching_letter = "M"
    match = AddressFactory(letter=matching_letter)
    AddressFactory(letter="XX")
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"), {"streetletter": matching_letter}
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match)],
    }


@mark.django_db
def test_filter_addresses_by_municipality():
    api_client = APIClient()
    municipality = MunicipalityFactory(name="Match")
    street = StreetFactory(municipality=municipality)
    match = AddressFactory(street=street)
    AddressFactory()
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"), {"municipality": municipality.name}
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match)],
    }


@mark.django_db
def test_filter_addresses_by_postal_code():
    api_client = APIClient()
    match = AddressFactory(postal_code="00100")
    AddressFactory(postal_code="99999")
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"), {"postalcode": match.postal_code}
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match)],
    }
