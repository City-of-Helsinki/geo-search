from django.conf import settings
from django.contrib.gis.geos import Point
from django.urls import reverse
from pytest import mark
from rest_framework.test import APIClient

from ..api.serializers import AddressSerializer
from ..tests.factories import (
    AddressFactory,
    MunicipalityFactory,
    PostalCodeAreaFactory,
    StreetFactory,
)


@mark.django_db
def test_get_address_list(api_client: APIClient):
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
def test_filter_addresses_by_street_name(api_client: APIClient):
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
def test_filter_addresses_by_street_number(api_client: APIClient):
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
def test_filter_addresses_by_street_letter(api_client: APIClient):
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
def test_filter_addresses_by_municipality(api_client: APIClient):
    municipality = MunicipalityFactory(name="Helsinki")
    match = AddressFactory(municipality=municipality)
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
def test_filter_addresses_by_municipality_code(api_client: APIClient):
    municipality = MunicipalityFactory(code="91")
    match = AddressFactory(municipality=municipality)
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"), {"municipalitycode": municipality.code}
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match)],
    }


@mark.django_db
def test_filter_addresses_by_postal_code(api_client: APIClient):
    postal_code_area = PostalCodeAreaFactory(postal_code="00100")
    PostalCodeAreaFactory(postal_code="99999")
    match = AddressFactory(postal_code_area=postal_code_area)
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"),
        {"postalcode": match.postal_code_area.postal_code},
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match)],
    }


@mark.django_db
def test_filter_addresses_by_post_office(api_client: APIClient):
    postal_code_area = PostalCodeAreaFactory(name="Askola")
    match = AddressFactory(postal_code_area=postal_code_area)
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"), {"postalcodearea": match.postal_code_area.name}
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match)],
    }


@mark.django_db
def test_filter_addresses_by_bbox(api_client: APIClient):
    match = AddressFactory(
        location=Point(x=24.9428, y=60.1666, srid=settings.PROJECTION_SRID)
    )
    AddressFactory(location=Point(x=27, y=67, srid=settings.PROJECTION_SRID))
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"), {"bbox": "24.9427,60.1665,24.9430,60.1667"}
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match)],
    }


@mark.django_db
def test_filter_addresses_by_bbox_returns_bad_request_if_bbox_is_invalid(
    api_client: APIClient,
):
    response = api_client.get(reverse("address:address-list"), {"bbox": "24.94,60.16"})
    assert response.status_code == 400


@mark.django_db
def test_filter_addresses_by_exact_location(api_client: APIClient):
    match = AddressFactory(
        location=Point(x=24.9428, y=60.1666, srid=settings.PROJECTION_SRID)
    )
    AddressFactory(location=Point(x=27, y=67, srid=settings.PROJECTION_SRID))
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"),
        {"lat": match.location.y, "lon": match.location.x},
    )
    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match)],
    }


@mark.django_db
def test_filter_addresses_by_location_with_distance(api_client: APIClient):
    lat, lon = 60.1666, 24.9428
    distance = 10
    matches = [
        # Exactly on the point
        AddressFactory(location=Point(x=lon, y=lat, srid=settings.PROJECTION_SRID)),
        # 9.8 meters away location, so should be included in the results
        AddressFactory(
            location=Point(x=24.942952094, y=60.16664523, srid=settings.PROJECTION_SRID)
        ),
    ]
    # 10.2 meters from the point, so should not be included in the results
    AddressFactory(
        location=Point(x=24.942984201, y=60.166600058, srid=settings.PROJECTION_SRID)
    )
    serializer = AddressSerializer()
    response = api_client.get(
        reverse("address:address-list"),
        {"lat": lat, "lon": lon, "distance": distance},
    )
    assert response.status_code == 200
    assert response.data == {
        "count": len(matches),
        "next": None,
        "previous": None,
        "results": [serializer.to_representation(match) for match in matches],
    }


@mark.django_db
def test_filter_addresses_returns_bad_request_if_location_is_invalid(
    api_client: APIClient,
):
    response = api_client.get(reverse("address:address-list"), {"lat": "60.1666"})
    assert response.status_code == 400


@mark.django_db
def test_filter_addresses_returns_bad_request_if_distance_is_invalid(
    api_client: APIClient,
):
    response = api_client.get(
        reverse("address:address-list"),
        {"lat": "60.1666", "lon": "24.9428", "distance": ""},
    )
    assert response.status_code == 400
