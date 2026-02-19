"""
This management command imports post office names from Posti's postal code data.

Posti provides postal code data in a ZIP file containing a fixed-width DAT file.
The format is documented at: https://www.posti.fi/en/for-businesses/customer-support/postal-code-services

Example URL: https://www.posti.fi/webpcode/PCF_20260218.zip

Usage:
    python manage.py import_post_offices path/to/PCF_YYYYMMDD.zip

Or provide a URL to download the file:
    python manage.py import_post_offices --url https://www.posti.fi/webpcode/PCF_20260218.zip
"""

import logging
import zipfile
from io import BytesIO
from pathlib import Path
from time import time

import requests
from django.core.management.base import BaseCommand, CommandError

from address.models import PostalCodeArea

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Imports post office names from Posti's postal code data."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "file",
            nargs="?",
            type=Path,
            help="Path to the ZIP file containing postal code data",
        )
        parser.add_argument(
            "--url",
            type=str,
            help="URL to download the postal code data from",
        )

    def handle(self, *args, **options) -> None:
        start_time = time()

        if options["url"]:
            zip_data = self._download_file(options["url"])
            num_updated = self._import_from_zip_bytes(zip_data)
        elif options["file"]:
            file_path = options["file"]
            if not file_path.exists():
                raise CommandError(f"File not found: {file_path}")
            self.stdout.write(f"Reading data from {file_path}.")
            num_updated = self._import_from_zip_file(file_path)
        else:
            raise CommandError(
                "You must provide either a file path or a URL using --url option"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{num_updated} postal code areas updated "
                f"in {time() - start_time:.0f} seconds."
            )
        )

    def _download_file(self, url: str) -> bytes:
        """Download the file from the given URL."""
        self.stdout.write(f"Downloading data from {url}...")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise CommandError(f"Failed to download file from {url}: {e}")

    def _import_from_zip_file(self, zip_path: Path) -> int:
        """Import post office names from a ZIP file."""
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_file:
                return self._import_from_zip(zip_file)
        except zipfile.BadZipFile as e:
            raise CommandError(f"Invalid ZIP file: {e}")

    def _import_from_zip_bytes(self, zip_data: bytes) -> int:
        """Import post office names from ZIP file bytes."""
        try:
            with zipfile.ZipFile(BytesIO(zip_data), "r") as zip_file:
                return self._import_from_zip(zip_file)
        except zipfile.BadZipFile as e:
            raise CommandError(f"Invalid ZIP file: {e}")

    def _import_from_zip(self, zip_file: zipfile.ZipFile) -> int:
        """Import post office names from an open ZIP file."""
        dat_files = [name for name in zip_file.namelist() if name.endswith(".dat")]

        if not dat_files:
            raise CommandError("No .dat file found in the ZIP archive")

        if len(dat_files) > 1:
            self.stdout.write(
                self.style.WARNING(f"Multiple .dat files found, using {dat_files[0]}")
            )

        dat_file = dat_files[0]
        self.stdout.write(f"Processing {dat_file}...")

        with zip_file.open(dat_file) as f:
            content = f.read()
            text = content.decode("latin-1")
            return self._import_post_offices(text)

    def _import_post_offices(self, content: str) -> int:
        """Import post office names from the DAT file content."""
        num_updated = 0

        for line_num, line in enumerate(content.splitlines(), start=1):
            if len(line) < 78:
                logger.debug(f"Line {line_num} too short, skipping")
                continue

            parsed_data = self._parse_line(line, line_num)
            if not parsed_data:
                continue

            postal_code, post_office_fi, post_office_sv, post_office_en = parsed_data
            num_updated += self._update_postal_code_areas(
                postal_code, post_office_fi, post_office_sv, post_office_en
            )

        return num_updated

    def _parse_line(self, line: str, line_num: int) -> tuple[str, str, str, str] | None:
        """Parse a line from the DAT file and return postal code
        and post office names."""
        # Parse fixed-width format
        # Positions 13-17: Postal code (5 digits)
        # Positions 18-47: Post office name in Finnish (30 chars)
        # Positions 48-77: Post office name in Swedish (30 chars)
        postal_code = line[13:18].strip()
        post_office_fi = line[18:48].strip()
        post_office_sv = line[48:78].strip()

        if not postal_code:
            logger.debug(f"Line {line_num}: Missing postal code")
            return None

        if not post_office_fi and not post_office_sv:
            logger.debug(
                f"Line {line_num}: Missing both Finnish and Swedish post office names"
            )
            return None

        # Use fallbacks: if Swedish is missing, use Finnish and vice versa
        if not post_office_fi:
            post_office_fi = post_office_sv
        if not post_office_sv:
            post_office_sv = post_office_fi

        # For English, use Finnish version
        post_office_en = post_office_fi

        return postal_code, post_office_fi, post_office_sv, post_office_en

    def _update_postal_code_areas(
        self,
        postal_code: str,
        post_office_fi: str,
        post_office_sv: str,
        post_office_en: str,
    ) -> int:
        """Update all postal code areas matching the given postal code."""
        try:
            postal_code_areas = PostalCodeArea.objects.filter(postal_code=postal_code)

            if not postal_code_areas.exists():
                logger.debug(f"No postal code area found for postal code {postal_code}")
                return 0

            num_updated = 0
            for area in postal_code_areas:
                area.set_current_language("fi")
                area.post_office = post_office_fi

                area.set_current_language("sv")
                area.post_office = post_office_sv

                area.set_current_language("en")
                area.post_office = post_office_en

                area.save()
                num_updated += 1
                logger.debug(
                    f"Updated postal code {postal_code} with post office "
                    f"FI:{post_office_fi} SV:{post_office_sv} EN:{post_office_en}"
                )

            return num_updated

        except Exception as e:
            logger.error(f"Error updating postal code {postal_code}: {e}")
            return 0
