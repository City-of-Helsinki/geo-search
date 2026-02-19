"""
Tests for querying addresses by post_office field.
"""

from django.urls import reverse
from pytest import mark
from rest_framework.test import APIClient

from address.tests.factories import AddressFactory, PostalCodeAreaFactory


@mark.django_db
def test_filter_addresses_by_post_office_finnish(api_client: APIClient):
    """Test filtering addresses by Finnish post office name."""
    postal_code_area = PostalCodeAreaFactory(postal_code="00900")
    postal_code_area.set_current_language("fi")
    postal_code_area.post_office = "HELSINKI"
    postal_code_area.save()

    address = AddressFactory(postal_code_area=postal_code_area)
    AddressFactory()  # Different postal code area

    url = reverse("address:address-list")
    response = api_client.get(url, {"postoffice": "HELSINKI"})

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["number"] == address.number


@mark.django_db
def test_filter_addresses_by_post_office_swedish(api_client: APIClient):
    """Test filtering addresses by Swedish post office name."""
    postal_code_area = PostalCodeAreaFactory(postal_code="00900")
    postal_code_area.set_current_language("sv")
    postal_code_area.post_office = "HELSINGFORS"
    postal_code_area.save()

    address = AddressFactory(postal_code_area=postal_code_area)
    AddressFactory()  # Different postal code area

    url = reverse("address:address-list")
    response = api_client.get(url, {"postoffice": "HELSINGFORS"})

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["number"] == address.number


@mark.django_db
def test_filter_addresses_by_post_office_case_insensitive(api_client: APIClient):
    """Test that post office filtering is case insensitive."""
    postal_code_area = PostalCodeAreaFactory(postal_code="00900")
    postal_code_area.set_current_language("fi")
    postal_code_area.post_office = "HELSINKI"
    postal_code_area.save()

    AddressFactory(postal_code_area=postal_code_area)

    url = reverse("address:address-list")
    response = api_client.get(url, {"postoffice": "helsinki"})

    assert response.status_code == 200
    assert response.data["count"] == 1


@mark.django_db
def test_filter_addresses_by_post_office_no_results(api_client: APIClient):
    """Test filtering by non-existent post office returns no results."""
    AddressFactory()

    url = reverse("address:address-list")
    response = api_client.get(url, {"postoffice": "NONEXISTENT"})

    assert response.status_code == 200
    assert response.data["count"] == 0


@mark.django_db
def test_filter_postal_code_areas_by_post_office(api_client: APIClient):
    """Test filtering postal code areas by post office name."""
    area1 = PostalCodeAreaFactory(postal_code="00900")
    area1.set_current_language("fi")
    area1.post_office = "HELSINKI"
    area1.save()

    area2 = PostalCodeAreaFactory(postal_code="02760")
    area2.set_current_language("fi")
    area2.post_office = "ESPOO"
    area2.save()

    url = reverse("address:postalcodearea-list")
    response = api_client.get(url, {"postoffice": "HELSINKI"})

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["postal_code"] == "00900"


@mark.django_db
def test_filter_addresses_combined_with_other_params(api_client: APIClient):
    """Test filtering by post office combined with other parameters."""
    postal_code_area = PostalCodeAreaFactory(postal_code="00900")
    postal_code_area.set_current_language("fi")
    postal_code_area.post_office = "HELSINKI"
    postal_code_area.save()

    AddressFactory(postal_code_area=postal_code_area, number="5")
    AddressFactory(postal_code_area=postal_code_area, number="10")

    url = reverse("address:address-list")
    response = api_client.get(url, {"postoffice": "HELSINKI", "streetnumber": "5"})

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["number"] == "5"
