from gisserver.features import FeatureType, ServiceDescription
from gisserver.geometries import CRS
from gisserver.views import WFSView

from ..models import Address

ETRS_TM35FIN = CRS.from_srid(3067)


class GeoWFSView(WFSView):

    xml_namespace = "https://paikkatietohaku.api.hel.fi/wfs"

    # The service metadata
    service_description = ServiceDescription(
        title="GeoSearch WFS",
        abstract="GeoSearch WFS service",
        keywords=["GeoSearch"],
        provider_name="City of Helsinki",
        provider_site="https://www.hel.fi/kanslia/fi",
    )

    feature_types = [
        FeatureType(Address.objects.all(), fields="__all__", other_crs=[ETRS_TM35FIN]),
    ]
