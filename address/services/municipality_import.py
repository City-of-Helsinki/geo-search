import logging
from django.conf import settings
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.geos import MultiPolygon
from typing import Iterable

from ..models import Address, Municipality

logger = logging.getLogger(__name__)


class MunicipalityImporter:
    def import_municipalities(self, features: Iterable[Feature]) -> int:
        """
        Import municipalities from given features to db.
        Also update address municipality according to municipality area.
        """
        total_municipalities_updated = 0
        total_addresses_updated = 0

        # Update municipality for all addresses within each postal code area
        for feature in features:
            geometry = feature.geom.geos
            code = feature["NATCODE"].value
            name_fi = feature["NAMEFIN"].value
            name_sv = feature["NAMESWE"].value
            municipality_id = name_fi.lower()

            municipality, _ = Municipality.objects.get_or_create(pk=municipality_id)
            municipality.set_current_language("sv")
            municipality.name = name_sv
            municipality.set_current_language("fi")
            municipality.name = name_fi
            municipality.id = municipality_id
            municipality.code = code
            if geometry.geom_type == "Polygon":
                area = MultiPolygon(geometry, srid=3067)
            else:
                area = geometry
            area.transform(settings.PROJECTION_SRID)
            municipality.area = area
            municipality.save()

            total_municipalities_updated += 1

            addresses = Address.objects.filter(
                location__intersects=geometry,
            )

            num_addresses_updated = addresses.update(municipality=municipality)

            logger.info(
                "%s, %s, %s, %s" % (code, name_fi, name_sv, num_addresses_updated)
            )
            total_addresses_updated += num_addresses_updated

        return total_addresses_updated
