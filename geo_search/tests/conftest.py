from pytest import fixture


@fixture
def authorization_required(settings):
    settings.REQUIRE_AUTHORIZATION = True


@fixture
def no_authorization_required(settings):
    settings.REQUIRE_AUTHORIZATION = False
