from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.db.models import Q, QuerySet
from rest_framework.exceptions import ParseError
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..models import Address
from .serializers import AddressSerializer


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
        # We have to do distinct here because filtering by the translated
        # fields can return the same object multiple times if it has multiple
        # translations (e.g. "fi" and "sv").
        return addresses.distinct()

    def _filter_by_street_name(self, addresses: QuerySet) -> QuerySet:
        street_name = self.request.query_params.get("streetname")
        if street_name is None:
            return addresses
        return addresses.filter(street__translations__name__iexact=street_name)

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
        )

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
