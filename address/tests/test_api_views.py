from django.urls import reverse
from pytest import mark
from rest_framework.test import APIClient

from ..api.serializers import AddressSerializer
from ..tests.factories import AddressFactory


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
