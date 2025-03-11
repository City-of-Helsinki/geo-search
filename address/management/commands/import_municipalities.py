"""
This management command imports municipalities from MML data:
https://www.maanmittauslaitos.fi/kartat-ja-paikkatieto/ammattilaiskayttajille/tuotekuvaukset/hallinnolliset-aluejaot-vektori
"""

from pathlib import Path
from time import time

from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand

from ...services.municipality_import import MunicipalityImporter


class Command(BaseCommand):
    help = "Import municipalities from the given MML shapefiles."

    def add_arguments(self, parser) -> None:
        parser.add_argument("files", nargs="+", type=Path)

    def handle(self, *args, **options) -> None:
        start_time = time()
        importer = MunicipalityImporter()
        paths = options["files"]
        num_addresses_updated = 0
        for path in paths:
            self.stdout.write(f"Reading data from {path}.")
            for layer in DataSource(path, encoding="utf-8"):
                num_addresses_updated += importer.import_municipalities(layer)
        self.stdout.write(
            self.style.SUCCESS(
                f"{num_addresses_updated} addresses updated "
                f"in {time() - start_time:.0f} seconds."
            )
        )
