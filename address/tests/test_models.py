from pytest import mark

from .factories import (
    AddressFactory,
    MunicipalityFactory,
    PostalCodeAreaFactory,
    StreetFactory,
)


@mark.django_db
def test_municipality_string_has_name():
    municipality = MunicipalityFactory()
    assert str(municipality) == municipality.name


@mark.django_db
def test_municipality_has_english_translation():
    municipality = MunicipalityFactory()
    municipality.set_current_language("en")
    assert municipality.name is not None
    assert municipality.has_translation("en")


@mark.django_db
def test_municipality_english_translation_can_be_different():
    municipality = MunicipalityFactory()
    municipality.set_current_language("fi")
    municipality.name = "Helsinki"
    municipality.set_current_language("en")
    municipality.name = "Helsinki City"
    municipality.save()

    municipality.set_current_language("fi")
    assert municipality.name == "Helsinki"
    municipality.set_current_language("en")
    assert municipality.name == "Helsinki City"


@mark.django_db
def test_street_string_has_name():
    street = StreetFactory()
    assert str(street) == street.name


@mark.django_db
def test_street_has_english_translation():
    street = StreetFactory()
    street.set_current_language("en")
    assert street.name is not None
    assert street.has_translation("en")


@mark.django_db
def test_street_english_translation_can_be_different():
    street = StreetFactory()
    street.set_current_language("fi")
    street.name = "Mannerheimintie"
    street.set_current_language("en")
    street.name = "Mannerheim Road"
    street.save()

    street.set_current_language("fi")
    assert street.name == "Mannerheimintie"
    street.set_current_language("en")
    assert street.name == "Mannerheim Road"


@mark.django_db
def test_postal_code_area_has_english_translation():
    postal_code_area = PostalCodeAreaFactory()
    postal_code_area.set_current_language("en")
    assert postal_code_area.name is not None
    assert postal_code_area.has_translation("en")


@mark.django_db
def test_postal_code_area_english_translation_can_be_different():
    postal_code_area = PostalCodeAreaFactory()
    postal_code_area.set_current_language("fi")
    postal_code_area.name = "Keskusta"
    postal_code_area.set_current_language("en")
    postal_code_area.name = "City Center"
    postal_code_area.save()

    postal_code_area.set_current_language("fi")
    assert postal_code_area.name == "Keskusta"
    postal_code_area.set_current_language("en")
    assert postal_code_area.name == "City Center"


@mark.django_db
def test_address_string_has_street_number_number_end_letter_municipality():
    address = AddressFactory()
    expected = (
        f"{address.street} {address.number}-{address.number_end}"
        f"{address.letter}, {address.municipality}"
    )
    assert str(address) == expected


@mark.django_db
def test_address_string_without_letter():
    address = AddressFactory(letter="")
    expected = (
        f"{address.street} {address.number}-{address.number_end}"
        f", {address.municipality}"
    )
    assert str(address) == expected


@mark.django_db
def test_address_string_without_number_end():
    address = AddressFactory(number_end="")
    expected = (
        f"{address.street} {address.number}{address.letter}, {address.municipality}"
    )
    assert str(address) == expected


@mark.django_db
def test_address_string_representation_without_number_end_and_letter():
    address = AddressFactory(number_end="", letter="")
    expected = f"{address.street} {address.number}, {address.municipality}"
    assert str(address) == expected
