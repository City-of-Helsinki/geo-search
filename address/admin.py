from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Address, Municipality, Street


class MunicipalityAdmin(TranslatableAdmin):
    pass


class StreetAdmin(TranslatableAdmin):
    pass


class AddressAdmin(admin.ModelAdmin):
    pass


admin.site.register(Municipality, MunicipalityAdmin)
admin.site.register(Street, StreetAdmin)
admin.site.register(Address, AddressAdmin)
