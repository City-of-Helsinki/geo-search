from typing import Any

from django.conf import settings
from django.http import HttpRequest
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey


class IsAuthorized(IsAuthenticated, HasAPIKey):
    """
    By default, this lets authenticated users (e.g. admin user logged in via
    Django admin) use and browse the API, while everybody else will have to
    use an API key. If settings.REQUIRE_AUTHORIZATION is False, then everybody
    has permission to use the API.
    """

    def has_permission(self, request: HttpRequest, view: Any) -> bool:
        if not settings.REQUIRE_AUTHORIZATION:
            return True
        is_authenticated = IsAuthenticated.has_permission(self, request, view)
        has_api_key = HasAPIKey.has_permission(self, request, view)
        return is_authenticated or has_api_key
