from django.conf import settings
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import D
from django.db.models import Q, QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from math import cos, pi
from rest_framework.exceptions import ParseError
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..models import Address
from .serializers import AddressSerializer

_list_parameters = [
    OpenApiParameter(
        name="streetname",
        location=OpenApiParameter.QUERY,
        description=(
            "Street name in Finnish or Swedish. "
            'E.g. "Mannerheimintie" or "Mannerheimvägen".'
        ),
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name="streetnumber",
        location=OpenApiParameter.QUERY,
        description='Street number, e.g. "42".',
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name="streetletter",
        location=OpenApiParameter.QUERY,
        description='Street letter, e.g. "B".',
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name="municipality",
        location=OpenApiParameter.QUERY,
        description=(
            "Municipality name in Finnish or Swedish. "
            'E.g. "Helsinki" or "Helsingfors".'
        ),
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name="postalcode",
        location=OpenApiParameter.QUERY,
        description='Postal code, e.g. "00100".',
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name="postoffice",
        location=OpenApiParameter.QUERY,
        description='Post office name, e.g. "Lappohja".',
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name="bbox",
        location=OpenApiParameter.QUERY,
        description=(
            'Bounding box in the format "left,bottom,right,top". '
            "Each value must be a floating point number or an integer."
        ),
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name="lat",
        location=OpenApiParameter.QUERY,
        description=(
            "Latitude (degrees) in the WGS84 (EPSG: 4326) coordinate system. "
            "If this parameter is given, then `lon` parameter must also be given."
        ),
        required=False,
        type=float,
    ),
    OpenApiParameter(
        name="lon",
        location=OpenApiParameter.QUERY,
        description=(
            "Longitude (degrees) in the WGS84 (EPSG: 4326) coordinate system. "
            "If this parameter is given, then `lat` parameter must also be given."
        ),
        required=False,
        type=float,
    ),
    OpenApiParameter(
        name="distance",
        location=OpenApiParameter.QUERY,
        description=(
            "Maximum distance (in meters) from the given location defined by"
            "the `lat` and `lon` parameters. By default, the value is `1`. "
            "If this parameter is given, the `lat` and `lon` parameters "
            "should also be given."
        ),
        required=False,
        type=float,
    ),
]


@extend_schema_view(list=extend_schema(parameters=_list_parameters))
class AddressViewSet(ReadOnlyModelViewSet):
    queryset = Address.objects.order_by("pk")
    serializer_class = AddressSerializer

    def get_queryset(self) -> QuerySet:
        addresses = self.queryset
        addresses = self._filter_by_street_name(addresses)
        addresses = self._filter_by_street_number(addresses)
        addresses = self._filter_by_street_letter(addresses)
        addresses = self._filter_by_municipality(addresses)
        addresses = self._filter_by_postal_code(addresses)
        addresses = self._filter_by_bbox(addresses)
        addresses = self._filter_by_location(addresses)
        return addresses

    def _filter_by_street_name(self, addresses: QuerySet) -> QuerySet:
        street_name = self.request.query_params.get("streetname")
        if street_name is None:
            return addresses
        return addresses.filter(
            street__translations__name__iexact=street_name
        ).distinct()

    def _filter_by_street_number(self, addresses: QuerySet) -> QuerySet:
        street_number = self.request.query_params.get("streetnumber")
        if street_number is None:
            return addresses
        return addresses.filter(
            Q(number__iexact=street_number) | Q(number_end__iexact=street_number)
        )

    def _filter_by_street_letter(self, addresses: QuerySet) -> QuerySet:
        street_letter = self.request.query_params.get("streetletter")
        if street_letter is None:
            return addresses
        return addresses.filter(letter__iexact=street_letter)

    def _filter_by_municipality(self, addresses: QuerySet) -> QuerySet:
        municipality = self.request.query_params.get("municipality")
        if municipality is None:
            return addresses
        return addresses.filter(
            street__municipality__translations__name__iexact=municipality
        ).distinct()

    def _filter_by_postal_code(self, addresses: QuerySet) -> QuerySet:
        postal_code = self.request.query_params.get("postalcode")
        if postal_code is None:
            return addresses
        return addresses.filter(postal_code__iexact=postal_code)

    def _filter_by_bbox(self, addresses: QuerySet) -> QuerySet:
        bbox = self.request.query_params.get("bbox")
        if bbox is None:
            return addresses
        try:
            polygon = Polygon.from_bbox(float(point) for point in bbox.split(","))
            polygon.srid = settings.PROJECTION_SRID
        except ValueError:
            raise ParseError(
                "bbox values must be floating points or integers "
                "in the format 'left,bottom,right,top'"
            )
        return addresses.filter(location__within=polygon)

    def _filter_by_location(self, addresses: QuerySet) -> QuerySet:
        lat = self.request.query_params.get("lat")
        lon = self.request.query_params.get("lon")
        if lat is None and lon is None:
            return addresses
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            raise ParseError("'lat' and 'lon' must be provided as numbers")
        try:
            distance = float(self.request.query_params.get("distance", 1))
        except ValueError:
            raise ParseError("'distance' must be a number")
        point = Point(lon, lat, srid=settings.PROJECTION_SRID)
        # WGS84 uses degrees as units, so for the buffer we need the approximate degrees
        distance_degrees = 2 * distance / 40000000 * 360 / cos(point.y / 360 * pi)
        # To make the address lookups faster, we first use a buffer to limit the
        # addresses to a smaller area. Then we can find the addresses by comparing
        # their distances to the point. This way we don't have to do the comparison
        # for every single address.
        buffer = point.buffer(distance_degrees)
        return addresses.filter(
            location__intersects=buffer,
            location__distance_lte=(point, D(m=distance)),
        )
