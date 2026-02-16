from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Municipality(TranslatableModel):
    id = models.CharField(_("Id"), max_length=100, primary_key=True)
    code = models.CharField(_("Municipality code"), max_length=3)
    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=100, db_index=True)
    )
    area = models.MultiPolygonField(
        _("Area"), srid=settings.PROJECTION_SRID, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Municipality")
        verbose_name_plural = _("Municipalities")


class Street(TranslatableModel):
    municipality = models.ForeignKey(
        Municipality, models.CASCADE, db_index=True, verbose_name=_("Municipality")
    )
    modified_at = models.DateTimeField(auto_now=True)
    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=100, db_index=True),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Street")
        verbose_name_plural = _("Streets")


class PostalCodeArea(TranslatableModel):
    postal_code = models.CharField(
        _("Postal code"), max_length=5, null=True, blank=True
    )
    municipality = models.ForeignKey(
        Municipality,
        models.CASCADE,
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_("Municipality"),
    )
    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=100, null=True, blank=True)
    )
    area = models.MultiPolygonField(
        _("Area"), srid=settings.PROJECTION_SRID, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.postal_code

    class Meta:
        verbose_name = _("Postal code area")
        verbose_name_plural = _("Postal code areas")


class Address(models.Model):
    municipality = models.ForeignKey(
        Municipality, models.CASCADE, db_index=True, verbose_name=_("Municipality")
    )
    street = models.ForeignKey(
        Street,
        models.CASCADE,
        db_index=True,
        related_name="addresses",
        verbose_name=_("Street"),
    )
    number = models.CharField(_("Number"), max_length=6, blank=True)
    number_end = models.CharField(_("Number end"), max_length=6, blank=True)
    letter = models.CharField(_("Letter"), max_length=2, blank=True)
    postal_code_area = models.ForeignKey(
        PostalCodeArea,
        models.CASCADE,
        null=True,
        blank=True,
        related_name="addresses",
        verbose_name=_("Postal code area"),
    )
    location = models.PointField(_("Location"), srid=settings.PROJECTION_SRID)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        s = f"{self.street} {self.number}"
        if self.number_end:
            s += f"-{self.number_end}"
        if self.letter:
            s += str(self.letter)
        return f"{s}, {self.municipality}"

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        indexes = [
            # This index speeds up address?municipality and address?municipalitycode
            # by 10x
            models.Index(
                name="idx_address_municipality_id",
                fields=["municipality", "id"],
                include=[
                    "street",
                    "number",
                    "number_end",
                    "letter",
                    "postal_code_area",
                    "location",
                    "modified_at",
                ],
            )
        ]
