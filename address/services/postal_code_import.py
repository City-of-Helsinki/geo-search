from django.contrib.gis.gdal.feature import Feature
from typing import Iterable

from ..models import Address


def import_postal_codes(features: Iterable[Feature]) -> int:
    """
    Go through the given postal code area features, find all addresses
    that are within each area, and update the postal code of the address
    accordingly.
    """
    total_addresses_updated = 0

    # Clear existing postal codes
    Address.objects.filter(postal_code__isnull=False).update(postal_code=None)

    # Update postal code for all addresses within each postal code area
    for feature in features:
        geometry = feature.geom.geos
        postal_code = feature["posti_alue"].value
        addresses = Address.objects.filter(
            postal_code__isnull=True,
            location__intersects=geometry,
        )
        num_addresses_updated = addresses.update(postal_code=postal_code)
        total_addresses_updated += num_addresses_updated

    return total_addresses_updated
