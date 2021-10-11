from django.urls import reverse


def test_openapi_schema(client):
    response = client.get(reverse("schema"))
    assert response.status_code == 200


def test_openapi_docs(client):
    response = client.get(reverse("schema-docs"))
    assert response.status_code == 200
