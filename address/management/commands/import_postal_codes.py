"""
This management command imports addresses from Paavo data:
https://www.stat.fi/org/avoindata/paikkatietoaineistot/paavo.html
"""

from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand
from pathlib import Path
from time import time

from ...services.postal_code_import import import_postal_codes


class Command(BaseCommand):
    help = "Imports postal codes from the given Paavo shapefiles."

    def add_arguments(self, parser) -> None:
        parser.add_argument("files", nargs="+", type=Path)

    def handle(self, *args, **options) -> None:
        start_time = time()
        paths = options["files"]
        num_addresses_updated = 0
        for path in paths:
            self.stdout.write(f"Reading data from {path}.")
            for layer in DataSource(path):
                num_addresses_updated += import_postal_codes(layer)
        self.stdout.write(
            self.style.SUCCESS(
                f"{num_addresses_updated} addresses updated "
                f"in {time() - start_time:.0f} seconds."
            )
        )
