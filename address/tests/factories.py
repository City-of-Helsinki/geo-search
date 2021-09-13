from factory import Faker, LazyAttribute, SubFactory
from factory.django import DjangoModelFactory

from ..models import Address, Municipality, Street


class MunicipalityFactory(DjangoModelFactory):
    id = LazyAttribute(lambda o: o.name.lower())
    name = Faker("city", locale="fi_FI")

    class Meta:
        model = Municipality


class StreetFactory(DjangoModelFactory):
    municipality = SubFactory(MunicipalityFactory)
    name = Faker("street_name", locale="fi_FI")

    class Meta:
        model = Street


class AddressFactory(DjangoModelFactory):
    street = SubFactory(StreetFactory)
    number = Faker("building_number", locale="fi_FI")
    number_end = Faker("building_number", locale="fi_FI")
    letter = Faker("random_uppercase_letter", locale="fi_FI")
    postal_code = Faker("postcode", locale="fi_FI")
    location = Faker("location", country_code="FI")

    class Meta:
        model = Address
