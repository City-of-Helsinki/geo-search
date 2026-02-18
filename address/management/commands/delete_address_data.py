"""
Deletes all address data from the database.
"""

from time import time

from django.core.management.base import BaseCommand

from address.models import Address, Municipality, PostalCodeArea, Street


class Command(BaseCommand):
    help = "Deletes all address data from the database."

    def handle(self, *args, **options) -> None:
        start_time = time()
        self.stdout.write("Deleting all address data...")
        Municipality.objects.all().delete()
        Street.objects.all().delete()
        Address.objects.all().delete()
        PostalCodeArea.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Address data deleted in {time() - start_time:.0f} seconds."
            )
        )
