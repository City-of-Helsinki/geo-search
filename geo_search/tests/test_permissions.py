from django.contrib.auth.models import User
from pytest import mark
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey


def test_anonymous_client_cannot_access_api_without_api_key():
    api_client = APIClient()
    response = api_client.get("/v1/")
    assert response.status_code == 403


def test_anonymous_client_can_access_api_if_authorization_is_not_required(
    no_authorization_required,
):
    api_client = APIClient()
    response = api_client.get("/v1/")
    assert response.status_code == 200


@mark.django_db
def test_anonymous_client_can_access_api_with_valid_api_key():
    valid_api_key = APIKey.objects.create_key(name="test")[-1]
    api_client = APIClient(HTTP_AUTHORIZATION=f"Api-Key {valid_api_key}")
    response = api_client.get("/v1/")
    assert response.status_code == 200


@mark.django_db
def test_anonymous_client_cannot_access_api_with_revoked_api_key():
    revoked_api_key = APIKey.objects.create_key(name="test", revoked=True)[-1]
    api_client = APIClient(HTTP_AUTHORIZATION=f"Api-Key {revoked_api_key}")
    response = api_client.get("/v1/")
    assert response.status_code == 403


@mark.django_db
def test_authenticated_client_can_access_api():
    user = User.objects.create()
    api_client = APIClient()
    api_client.force_authenticate(user)
    response = api_client.get("/v1/")
    assert response.status_code == 200
