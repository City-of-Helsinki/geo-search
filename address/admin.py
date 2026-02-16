from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from .models import Address, Municipality, PostalCodeArea, Street


@admin.register(Municipality)
class MunicipalityAdmin(TranslatableAdmin):
    list_display = ("id", "code")
    ordering = ("id",)
    search_fields = ("id",)


@admin.register(Street)
class StreetAdmin(TranslatableAdmin):
    list_display = ("name_column", "municipality")
    search_fields = ("translations__name",)

    @admin.display(description=_("Name"))
    def name_column(self, object):
        return object.name

    def get_queryset(self, request):
        language_code = self.get_queryset_language(request)
        return (
            super()
            .get_queryset(request)
            .translated(language_code)
            .order_by("translations__name")
        )


@admin.register(PostalCodeArea)
class PostalCodeAreaAdmin(TranslatableAdmin):
    list_display = ("postal_code", "name", "municipality")
    ordering = ("postal_code",)
    search_fields = ("postal_code",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("street", "number", "municipality", "postal_code_area")
    raw_id_fields = ["street"]
    ordering = ("street", "number", "municipality")
    search_fields = ("street__translations__name",)
