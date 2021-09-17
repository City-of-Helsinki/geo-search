from rest_framework.viewsets import ReadOnlyModelViewSet

from ..models import Address
from .serializers import AddressSerializer


class AddressViewSet(ReadOnlyModelViewSet):
    queryset = Address.objects.order_by("pk")
    serializer_class = AddressSerializer
