import logging
from collections.abc import Iterable

from django.conf import settings
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.geos import MultiPolygon

from address.constants import MUNICIPALITIES

from ..models import Address, Municipality, PostalCodeArea
from .import_utils import value_or_empty

logger = logging.getLogger(__name__)


class PostalCodeImporter:
    def __init__(self, province: str = None):
        self.province = province

    def import_postal_codes(self, features: Iterable[Feature]) -> int:
        """
        Go through the given postal code area features, find all addresses
        that are within each area, and update the postal code of the address
        accordingly.
        """
        total_addresses_updated = 0

        if self.province in MUNICIPALITIES.keys():
            muni_ids = [
                muni[1][0].lower() for muni in MUNICIPALITIES[self.province].items()
            ]
            # Clear existing postal code areas for one province
            Address.objects.filter(
                postal_code_area__isnull=False, municipality__id__in=muni_ids
            ).update(
                postal_code_area=None,
            )
        else:
            # Clear existing postal code areas for all provinces
            Address.objects.filter(postal_code_area__isnull=False).update(
                postal_code_area=None,
            )

        # Update postal code for all addresses within each postal code area
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
            municipality_id = int(value_or_empty(feature, "kuntanro"))

            postal_code_area, _ = PostalCodeArea.objects.get_or_create(
                postal_code=postal_code
            )
            postal_code_area.set_current_language("en")
            postal_code_area.name = post_office_fi
            postal_code_area.set_current_language("sv")
            postal_code_area.name = post_office_sv
            postal_code_area.set_current_language("fi")
            postal_code_area.name = post_office_fi

            try:
                municipality = Municipality.objects.filter(code=municipality_id).first()
            except Municipality.DoesNotExist:
                municipality = None
            postal_code_area.municipality = municipality

            if geometry.geom_type == "Polygon":
                area = MultiPolygon(geometry, srid=3067)
            else:
                area = geometry
            area.transform(settings.PROJECTION_SRID)
            postal_code_area.area = area
            postal_code_area.save()

            addresses = Address.objects.filter(
                postal_code_area__isnull=True,
                location__intersects=geometry,
            )

            num_addresses_updated = addresses.update(postal_code_area=postal_code_area)

            logger.info(
                "%s, %s, %s, %s"
                % (postal_code, post_office_fi, post_office_sv, num_addresses_updated)
            )

            total_addresses_updated += num_addresses_updated

        return total_addresses_updated
