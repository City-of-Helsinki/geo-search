from gisserver.features import FeatureType, ServiceDescription
from gisserver.geometries import CRS
from gisserver.views import WFSView

from ..models import Address, Municipality, PostalCodeArea

ETRS_TM35FIN = CRS.from_srid(3067)


class GeoWFSView(WFSView):
    xml_namespace = "https://paikkatietohaku.api.hel.fi/wfs"

    # The service metadata
    service_description = ServiceDescription(
        title="GeoSearch",
        abstract="GeoSearch WFS service",
        keywords=["GeoSearch"],
        provider_name="City of Helsinki",
        provider_site="https://www.hel.fi/",
    )

    feature_types = [
        FeatureType(Address.objects.all(), fields="__all__", other_crs=[ETRS_TM35FIN]),
        FeatureType(
            Municipality.objects.all(), fields="__all__", other_crs=[ETRS_TM35FIN]
        ),
        FeatureType(
            PostalCodeArea.objects.all(), fields="__all__", other_crs=[ETRS_TM35FIN]
        ),
    ]
