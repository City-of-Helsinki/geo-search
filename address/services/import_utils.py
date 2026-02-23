from functools import lru_cache

from django.contrib.gis.gdal.feature import Feature

from address.models import Municipality


def value_or_empty(feature: Feature, key: str) -> str:
    field = feature[key]
    if not field or field.value is None:
        return ""
    value = field.value
    if isinstance(value, int):
        return str(value)
    return value.strip() if isinstance(value, str) else str(value)


@lru_cache(maxsize=None)  # noqa: B019
def create_municipality(
    code: str, municipality_fi: str, municipality_sv: str, municipality_en: str
) -> Municipality:
    """Create a new municipality if it does not exist already, and return it.

    Args:
        code: 3-character municipality code (e.g., "091" for Helsinki)
        municipality_fi: Finnish name
        municipality_sv: Swedish name
        municipality_en: English name
    """
    municipality, _ = Municipality.objects.get_or_create(id=municipality_fi.lower())
    municipality.set_current_language("en")
    municipality.name = municipality_en
    municipality.set_current_language("sv")
    municipality.name = municipality_sv
    municipality.set_current_language("fi")
    municipality.name = municipality_fi
    municipality.code = code
    municipality.save()
    return municipality
