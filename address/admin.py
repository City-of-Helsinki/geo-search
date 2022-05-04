from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Address, Municipality, PostalCodeArea, Street


@admin.register(Municipality)
class MunicipalityAdmin(TranslatableAdmin):
    pass


@admin.register(Street)
class StreetAdmin(TranslatableAdmin):
    pass


@admin.register(PostalCodeArea)
class PostalCodeAreaAdmin(TranslatableAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    raw_id_fields = ["street"]
