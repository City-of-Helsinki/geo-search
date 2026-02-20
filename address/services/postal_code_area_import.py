import logging
from collections.abc import Iterable

from django.conf import settings
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.geos import MultiPolygon

from ..models import Address, PostalCodeArea
from .import_utils import value_or_empty

logger = logging.getLogger(__name__)

POSTAL_CODE_AREA_SOURCE_SRID = 3067


class PostalCodeAreaImporter:
    @staticmethod
    def import_postal_code_areas(features: Iterable[Feature]) -> int:
        """
        Go through the given postal code area features
        and create/update PostalCodeArea objects for each area.

        Also find all addresses that are within each area
        and update the postal code area of the address.
        """
        total_addresses_updated = 0

        # Update postal code area for all addresses within each postal code area
        for feature in features:
            geometry = feature.geom.geos
            postal_code = value_or_empty(feature, "posti_alue")
            if not postal_code:
                logger.warning("Postal code area with no postal code, skipping")
                continue
            post_office_fi = value_or_empty(feature, "nimi")
            post_office_sv = value_or_empty(feature, "namn") or post_office_fi
            if not post_office_fi:
                post_office_fi = post_office_sv

            postal_code_area, _ = PostalCodeArea.objects.get_or_create(
                postal_code=postal_code
            )
            postal_code_area.set_current_language("en")
            postal_code_area.name = post_office_fi
            postal_code_area.set_current_language("sv")
            postal_code_area.name = post_office_sv
            postal_code_area.set_current_language("fi")
            postal_code_area.name = post_office_fi

            if geometry.geom_type == "Polygon":
                area = MultiPolygon(geometry, srid=POSTAL_CODE_AREA_SOURCE_SRID)
            else:
                area = geometry
            area.transform(settings.PROJECTION_SRID)
            postal_code_area.area = area
            postal_code_area.save()

            addresses = Address.objects.filter(
                location__intersects=geometry,
            )

            num_addresses_updated = addresses.update(postal_code_area=postal_code_area)

            logger.info(
                "%s, %s, %s, %s"
                % (postal_code, post_office_fi, post_office_sv, num_addresses_updated)
            )

            total_addresses_updated += num_addresses_updated

        return total_addresses_updated
