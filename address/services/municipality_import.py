import logging
from collections.abc import Iterable

from django.conf import settings
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.geos import MultiPolygon

from ..models import Address
from .import_utils import create_municipality, value_or_empty

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
            code = int(value_or_empty(feature, "NATCODE"))
            name_fi = value_or_empty(feature, "NAMEFIN")
            name_sv = value_or_empty(feature, "NAMESWE") or name_fi
            if not name_fi and not name_sv:
                logger.warning(f"Municipality with code {code} has no name, skipping")
                continue

            if not name_fi:
                name_fi = name_sv

            municipality = create_municipality(
                code=code,
                municipality_fi=name_fi,
                municipality_sv=name_sv,
                municipality_en=name_fi,
            )
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

            logger.info(f"{code}, {name_fi}, {name_sv}, {num_addresses_updated}")
            total_addresses_updated += num_addresses_updated

        return total_addresses_updated
