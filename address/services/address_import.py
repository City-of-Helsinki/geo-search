from bisect import bisect_left
from collections.abc import Iterable
from functools import lru_cache
from math import sqrt

from django.conf import settings
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.geos import LineString, MultiPoint, Point

from address.constants import MUNICIPALITIES
from address.models import Address, Municipality, Street
from address.services.import_utils import create_municipality, value_or_empty

# Offset (in meters) from the middle of the street to the address at perpendicular to
# the street. Setting this to zero makes the address locations lie exactly on the street
# link. Increasing it will push them further from the street. This relies on the fact
# that Digiroad data uses ETRS-TM35FIN (EPSG: 3067) which has meters as the unit.
ADDRESS_LOCATION_OFFSET_METERS = 15

# Write addresses to database after this many instances have been generated
ADDRESS_BATCH_SIZE = 1000

ADDRESS_SOURCE_SRID = 3067


def _transform_address_locations(addresses: list[Address]) -> None:
    """
    Transforms the locations of each given address to the projection given in
    settings.The points are transformed in bulk through a MultiPoint because
    it's significantly faster than transforming each point individually.
    """
    if not addresses:
        return
    locations = [address.location for address in addresses]
    transformed_points = MultiPoint(locations, srid=ADDRESS_SOURCE_SRID)
    transformed_points.transform(settings.PROJECTION_SRID)
    for i, address in enumerate(addresses):
        address.location = transformed_points[i]


def _find_numbers(feature: Feature, right_side: bool = False) -> range:
    """Find the numbers on the given side of the street from the feature."""
    # Get first and last building numbers on this side of the street from the
    # feature
    if right_side:
        first_number = feature["ENS_TALO_O"].value
        last_number = feature["VIIM_TAL_O"].value
    else:
        first_number = feature["ENS_TALO_V"].value
        last_number = feature["VIIM_TAL_V"].value

    if first_number is None or last_number is None:
        return range(0)  # This side of the street has no buildings

    # Depending on the digitizing direction, for some street links
    # the last and first number might be in the opposite order.
    if last_number < first_number:
        number_increment = -2
        last_number_offset = -1
    else:
        number_increment = 2
        last_number_offset = 1

    return range(first_number, last_number + last_number_offset, number_increment)


def _compute_normals(line_string: LineString) -> dict[float, tuple[float, float]]:
    """
    Compute a lookup table for the normals for each line segment in the line string.
    This is done so that given an interpolated distance (between 0 and 1) on the
    line string, we can quickly find the normal at that distance.
    """
    normals = {}
    start_x, start_y = line_string[0][:2]
    for end_x, end_y, *_ in line_string[1:]:
        if (end_x, end_y) == line_string[-1][:2]:
            distance = 1  # Make sure distance 1 ends at the last point
        else:
            distance = line_string.project_normalized(Point(end_x, end_y))
        # Calculate the normal
        dx = end_x - start_x
        dy = end_y - start_y
        length = sqrt(dx**2 + dy**2)
        normal = -dy / length, dx / length
        # Associate with the distance for fast lookup of the
        # normal between the current start point and end point.
        normals[distance] = normal
        start_x, start_y = end_x, end_y
    return normals


def _find_normal(
    distance: float, normals: dict, opposite: bool = False
) -> tuple[float, float]:
    """
    Given an distance between 0 and 1 on the line string, find the normal
    (or its opposite) from the provided dictionary.
    """
    distances = list(normals.keys())
    distance_index = bisect_left(distances, distance)
    normal_index = distances[distance_index]
    x, y = normals[normal_index]
    # If we are creating addresses for the right side of the street,
    # we need the normal pointing in the opposite direction.
    if opposite:
        return -x, -y
    return x, y


def _has_required_fields(feature: Feature) -> bool:
    """Check whether the feature contains street name, first/last numbers
    and municipality code.
    """
    street_keys = ["TIENIMI_SU", "TIENIMI_RU"]
    number_keys = ["ENS_TALO_O", "ENS_TALO_V", "VIIM_TAL_O", "VIIM_TAL_V"]
    municipality_key = "KUNTAKOODI"
    has_street = any(feature[key].value for key in street_keys)
    has_number = any(feature[key].value for key in number_keys)
    has_municipality = feature[municipality_key].value
    return has_street and has_number and has_municipality


def _build_addresses_on_side(
    street: Street,
    municipality: Municipality,
    feature: Feature,
    normals: dict[float, tuple[float, float]],
    right_side: bool,
) -> list[Address]:
    """Constructs addresses for one side (right or left) of a street."""
    numbers = _find_numbers(feature, right_side)
    if not numbers:
        return []  # No buildings on this side of the street

    # The street numbers are spread evenly to the length of the street link. This
    # means that if there is only one number, the address location will be in the
    # middle (normalized distance 0.5) of the line segment. If there are two
    # numbers, they will be at distance 0.25 and 0.75, and so on.
    interval = 1.0 / len(numbers)
    start_distance = interval / 2

    line_string = feature.geom.geos
    addresses = []
    for i, number in enumerate(numbers):
        # Distance between 0 and 1 on the line string where the address should
        # be placed
        distance = start_distance + i * interval

        # To be able to translate the location towards the side of the street,
        # we need to find the normal of the street at the given distance.
        normal_x, normal_y = _find_normal(distance, normals, right_side)

        # Now we can find the exact point on the line string at the given distance,
        # and translate it along the normal.
        street_location = line_string.interpolate_normalized(distance)
        location = Point(
            x=street_location.x + normal_x * ADDRESS_LOCATION_OFFSET_METERS,
            y=street_location.y + normal_y * ADDRESS_LOCATION_OFFSET_METERS,
            srid=street_location.srid,
        )
        addresses.append(
            Address(
                street=street,
                municipality=municipality,
                number=number,
                location=location,
            )
        )

    return addresses


class AddressImporter:
    def __init__(self, province: str = None):
        self.province = province

    def delete_address_data(self) -> None:
        """Delete the existing address-related data."""
        if self.province in MUNICIPALITIES.keys():
            muni_ids = [
                muni[1][0].lower() for muni in MUNICIPALITIES[self.province].items()
            ]
            Street.objects.filter(addresses__municipality_id__in=muni_ids).delete()
            Address.objects.filter(municipality_id__in=muni_ids).delete()

    def import_addresses(self, features: Iterable[Feature]) -> int:
        """Create addresses from the given features."""
        addresses = []
        num_addresses = 0
        for _i, feature in enumerate(features, start=1):
            feature_addresses = self._build_addresses_from_feature(feature)
            num_addresses += len(feature_addresses)
            addresses.extend(feature_addresses)
            if len(addresses) > ADDRESS_BATCH_SIZE:
                _transform_address_locations(addresses)
                Address.objects.bulk_create(addresses)
                addresses.clear()

        _transform_address_locations(addresses)
        Address.objects.bulk_create(addresses)
        return num_addresses

    def _build_addresses_from_feature(self, feature: Feature) -> list[Address]:
        """Construct addresses from the given feature."""
        if not _has_required_fields(feature):
            return []

        municipality = self._get_municipality(feature)
        if municipality is None:
            return []

        street_name_fi = value_or_empty(feature, "TIENIMI_SU")
        street_name_sv = value_or_empty(feature, "TIENIMI_RU") or street_name_fi
        if not street_name_fi:
            street_name_fi = street_name_sv

        street = self._create_street(
            street_name_fi,
            street_name_sv,
            street_name_fi,
            municipality,
        )

        # Calculate a lookup table for the normals to avoid computing
        # them multiple times for the same geometry.
        normals = _compute_normals(feature.geom.geos.simplify())

        # Construct addresses for each side of the street. They have to be done
        # separately since each side may have a different number of addresses.
        addresses = _build_addresses_on_side(
            street, municipality, feature, normals, right_side=True
        )
        addresses += _build_addresses_on_side(
            street, municipality, feature, normals, right_side=False
        )
        return addresses

    @lru_cache(maxsize=None)  # noqa: B019
    def _create_street(
        self, name_fi: str, name_sv: str, name_en: str, municipality: Municipality
    ) -> Street:
        """Create a new street if it does not exist already, and return it."""
        street, _ = Street.objects.translated(name=name_fi).get_or_create(
            municipality=municipality
        )
        street.set_current_language("en")
        street.name = name_en
        street.set_current_language("sv")
        street.name = name_sv
        street.set_current_language("fi")
        street.name = name_fi
        street.save()
        return street

    def _get_municipality(self, feature: Feature) -> Municipality | None:
        """Parse and validate municipality code from feature and return a
        Municipality instance, or None if the code is missing or unknown.
        """
        raw = value_or_empty(feature, "KUNTAKOODI")
        try:
            municipality_code = str(int(raw)).zfill(3)
        except ValueError:
            return None
        if municipality_code not in MUNICIPALITIES[self.province]:
            return None
        municipality_fi, municipality_sv = MUNICIPALITIES[self.province][
            municipality_code
        ]
        return create_municipality(
            municipality_code, municipality_fi, municipality_sv, municipality_fi
        )
