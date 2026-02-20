"""
This management command imports addresses from Paavo data
(Statistics Finland's open data on postal code areas).

The data can be downloaded from:
https://www.stat.fi/org/avoindata/paikkatietoaineistot/paavo.html
"""

from pathlib import Path
from time import time

from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand

from ...services.postal_code_area_import import PostalCodeAreaImporter


class Command(BaseCommand):
    help = "Imports postal code areas from the given Paavo shapefiles."

    def add_arguments(self, parser) -> None:
        parser.add_argument("files", nargs="+", type=Path)

    def handle(self, *args, **options) -> None:
        start_time = time()
        paths = options["files"]
        num_addresses_updated = 0
        for path in paths:
            self.stdout.write(f"Reading data from {path}.")
            for layer in DataSource(path, encoding="latin-1"):
                num_addresses_updated += (
                    PostalCodeAreaImporter().import_postal_code_areas(layer)
                )
        self.stdout.write(
            self.style.SUCCESS(
                f"{num_addresses_updated} addresses updated "
                f"in {time() - start_time:.0f} seconds."
            )
        )
