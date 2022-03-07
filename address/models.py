from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext as _
from parler.models import TranslatableModel, TranslatedFields


class Municipality(TranslatableModel):
    id = models.CharField(max_length=100, primary_key=True)
    code = models.CharField(max_length=3)
    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=100, db_index=True)
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = _("Municipalities")


class Street(TranslatableModel):
    municipality = models.ForeignKey(Municipality, models.CASCADE, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)
    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=100, db_index=True),
    )

    def __str__(self) -> str:
        return self.name


class Address(models.Model):
    street = models.ForeignKey(
        Street, models.CASCADE, db_index=True, related_name="addresses"
    )
    number = models.CharField(max_length=6, blank=True)
    number_end = models.CharField(max_length=6, blank=True)
    letter = models.CharField(max_length=2, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    post_office = models.CharField(max_length=100, null=True, blank=True)
    location = models.PointField(srid=settings.PROJECTION_SRID)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        s = f"{self.street} {self.number}"
        if self.number_end:
            s += f"-{self.number_end}"
        if self.letter:
            s += str(self.letter)
        return f"{s}, {self.street.municipality}"

    class Meta:
        verbose_name_plural = _("addresses")
