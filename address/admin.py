from django.contrib import admin
from django.forms import ModelForm
from parler.admin import TranslatableAdmin

from .models import Address, Municipality, Street


class AddressAdminForm(ModelForm):
    """
    An admin form for addresses that prefetches translations.
    This is need to keep the Django admin interface responsive
    when there are thousands of addresses.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["street"].queryset = self.fields[
            "street"
        ].queryset.prefetch_related("translations")


@admin.register(Municipality)
class MunicipalityAdmin(TranslatableAdmin):
    pass


@admin.register(Street)
class StreetAdmin(TranslatableAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    form = AddressAdminForm
