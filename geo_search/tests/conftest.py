from pytest import fixture


@fixture
def no_authorization_required(settings):
    settings.REQUIRE_AUTHORIZATION = False
