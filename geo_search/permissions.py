from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

# This lets authenticated users (e.g. admin user logged in via Django admin)
# use and browse the API, while everybody else will have to use an API key.
IsAuthenticatedOrHasAPIKey = IsAuthenticated | HasAPIKey
