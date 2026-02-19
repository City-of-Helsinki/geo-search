"""
Tests for PostalCodeArea API with post_office field.
"""

from django.urls import reverse
from pytest import mark
from rest_framework.test import APIClient

from address.tests.factories import PostalCodeAreaFactory


@mark.django_db
def test_postal_code_area_api_includes_post_office_translations(api_client: APIClient):
    """Test that the API returns post_office in all languages."""
    area = PostalCodeAreaFactory(postal_code="00900")

    area.set_current_language("fi")
    area.name = "Helsinki Keskusta"
    area.post_office = "HELSINKI"

    area.set_current_language("sv")
    area.name = "Helsingfors Centrum"
    area.post_office = "HELSINGFORS"

    area.set_current_language("en")
    area.name = "Helsinki Centre"
    area.post_office = "HELSINKI"

    area.save()

    url = reverse("address:postalcodearea-detail", kwargs={"pk": area.pk})
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()

    assert data["postal_code"] == "00900"

    assert "post_office" in data
    assert data["post_office"]["fi"] == "HELSINKI"
    assert data["post_office"]["sv"] == "HELSINGFORS"
    assert data["post_office"]["en"] == "HELSINKI"

    assert "name" in data
    assert data["name"]["fi"] == "Helsinki Keskusta"
    assert data["name"]["sv"] == "Helsingfors Centrum"
    assert data["name"]["en"] == "Helsinki Centre"
