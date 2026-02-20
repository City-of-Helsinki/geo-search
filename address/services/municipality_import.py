import logging
from collections.abc import Iterable

from django.conf import settings
from django.contrib.gis.gdal.feature import Feature
from django.contrib.gis.geos import MultiPolygon

from ..models import Address
from .import_utils import create_municipality, value_or_empty

logger = logging.getLogger(__name__)

MUNICIPALITY_SOURCE_SRID = 3067


class MunicipalityImporter:
    @staticmethod
    def import_municipalities(features: Iterable[Feature]) -> int:
        """
        Import municipalities from given features to db.
        Also update address municipality according to municipality area.
        """
        total_municipalities_updated = 0
        total_addresses_updated = 0

        # Update municipality for all addresses within each postal code area
        for feature in features:
            validated_data = MunicipalityImporter._extract_and_validate_fields(feature)
            if not validated_data:
                continue

            code, name_fi, name_sv = validated_data
            geometry = feature.geom.geos

            municipality = create_municipality(
                code=code,
                municipality_fi=name_fi,
                municipality_sv=name_sv,
                municipality_en=name_fi,
            )
            if geometry.geom_type == "Polygon":
                area = MultiPolygon(geometry, srid=MUNICIPALITY_SOURCE_SRID)
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

    @staticmethod
    def _extract_and_validate_fields(
        feature: Feature,
    ) -> tuple[int, str, str] | None:
        """Extract and validate required municipality fields from feature.

        Returns:
            Tuple of (code, name_fi, name_sv) if all validations pass,
            None if any validation fails.

        Required fields:
        - NATCODE: Municipality code (must be valid integer)
        - NAMEFIN or NAMESWE: Municipality name in Finnish or Swedish
        """
        nat_code = value_or_empty(feature, "NATCODE")
        code = None

        if not nat_code:
            logger.warning("Municipality feature missing NATCODE, skipping")
        else:
            try:
                code = int(nat_code)
            except ValueError:
                logger.warning(f"Invalid NATCODE value '{nat_code}', skipping")

        if code is None:
            return None

        name_fi = value_or_empty(feature, "NAMEFIN")
        name_sv = value_or_empty(feature, "NAMESWE")

        if not name_fi and not name_sv:
            logger.warning(f"Municipality with code {nat_code} has no name, skipping")
            return None

        # Apply fallbacks
        if not name_sv:
            name_sv = name_fi
        if not name_fi:
            name_fi = name_sv

        return code, name_fi, name_sv
