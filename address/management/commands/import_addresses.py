"""
This management command imports addresses from Digiroad shapefiles (DR_LINKKI.shp).

The Digiroad data uses ETRS-TM35FIN projection (EPSG: 3067) and the street geometries
are of type "LINESTRING ZM". This geometry type is not supported by GeoDjango, so the
data needs to be first converted to a supported format. Easiest is to remove the
M coordinate, which is not required anyway for calculating the address locations:

    ogr2ogr -f "ESRI Shapefile" DR_LINKKI_converted.shp DR_LINKKI.shp -dim XYZ

After this, the shapefiles can be given to the management command as arguments:

    python manage.py import_addresses somepath/DR_LINKKI.shp another/DR_LINKKI.shp

Each shapefile is processed and addresses (including streets and municipalities)
are created from the features.
"""

from pathlib import Path
from time import time

from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand

from ...services.address_import import AddressImporter


class Command(BaseCommand):
    help = "Imports addresses from the given Digiroad shapefiles."

    def add_arguments(self, parser) -> None:
        parser.add_argument("files", nargs="+", type=Path)
        parser.add_argument("province")

    def handle(self, *args, **options) -> None:
        start_time = time()
        self.stdout.write(f"Deleting existing data for province {options['province']}.")
        importer = AddressImporter(options["province"])
        importer.delete_address_data()
        paths = options["files"]
        total_addresses = 0
        for path in paths:
            self.stdout.write(f"Reading data from {path}.")
            for layer in DataSource(path):
                num_addresses = importer.import_addresses(layer)
                total_addresses += num_addresses
                self.stdout.write(f"{num_addresses} addresses imported from {path}.")
        self.stdout.write(
            self.style.SUCCESS(
                f"{total_addresses} addresses imported "
                f"in {time() - start_time:.0f} seconds."
            )
        )
