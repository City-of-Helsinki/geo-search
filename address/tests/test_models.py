from pytest import mark

from .factories import AddressFactory, MunicipalityFactory, StreetFactory


@mark.django_db
def test_municipality_string_has_name():
    municipality = MunicipalityFactory()
    assert str(municipality) == municipality.name


@mark.django_db
def test_street_string_has_name():
    street = StreetFactory()
    assert str(street) == street.name


@mark.django_db
def test_address_string_has_street_number_number_end_letter_municipality():
    address = AddressFactory()
    expected = (
        f"{address.street} {address.number}-{address.number_end}"
        f"{address.letter}, {address.street.municipality}"
    )
    assert str(address) == expected


@mark.django_db
def test_address_string_without_letter():
    address = AddressFactory(letter="")
    expected = (
        f"{address.street} {address.number}-{address.number_end}"
        f", {address.street.municipality}"
    )
    assert str(address) == expected


@mark.django_db
def test_address_string_without_number_end():
    address = AddressFactory(number_end="")
    expected = (
        f"{address.street} {address.number}{address.letter}"
        f", {address.street.municipality}"
    )
    assert str(address) == expected


@mark.django_db
def test_address_string_representation_without_number_end_and_letter():
    address = AddressFactory(number_end="", letter="")
    expected = f"{address.street} {address.number}, {address.street.municipality}"
    assert str(address) == expected
