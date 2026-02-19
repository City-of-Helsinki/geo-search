"""
Tests for the import_post_offices management command.
"""

import zipfile
from pathlib import Path

from django.core.management import call_command
from pytest import mark

from address.models import PostalCodeArea
from address.tests.factories import PostalCodeAreaFactory


def create_test_zip(zip_path: Path, postal_data: list[tuple[str, str, str]]) -> None:
    """
    Create a test ZIP file with Posti fixed-width format DAT file.

    Args:
        zip_path: Path where the ZIP file should be created
        postal_data: List of tuples (postal_code, post_office_fi, post_office_sv)
    """
    lines = []
    for postal_code, post_office_fi, post_office_sv in postal_data:
        # Build a fixed-width line
        # Positions 0-12: Header (PONOT20260218)
        # Positions 13-17: Postal code (5 chars)
        # Positions 18-47: Finnish post office (30 chars)
        # Positions 48-77: Swedish post office (30 chars)
        line = (
            "PONOT20260218"
            + postal_code.ljust(5)
            + post_office_fi.ljust(30)
            + post_office_sv.ljust(30)
        )
        # Pad to minimum length
        line = line.ljust(200)
        lines.append(line)

    dat_content = "\n".join(lines)

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("PCF_20260218.dat", dat_content)


@mark.django_db
def test_import_post_offices_from_zip_file(tmp_path):
    """Test importing post office names from a ZIP file with Finnish and Swedish."""
    area1 = PostalCodeAreaFactory(postal_code="00900")
    area2 = PostalCodeAreaFactory(postal_code="02760")
    area3 = PostalCodeAreaFactory(postal_code="07590")

    zip_file = tmp_path / "postal_codes.zip"
    create_test_zip(
        zip_file,
        [
            ("00900", "HELSINKI", "HELSINGFORS"),
            ("02760", "ESPOO", "ESBO"),
            ("07590", "ASKOLA", "ASKOLA"),
        ],
    )

    call_command("import_post_offices", str(zip_file))

    area1.refresh_from_db()
    area1.set_current_language("fi")
    assert area1.post_office == "HELSINKI"
    area1.set_current_language("sv")
    assert area1.post_office == "HELSINGFORS"
    area1.set_current_language("en")
    assert area1.post_office == "HELSINKI"

    area2.refresh_from_db()
    area2.set_current_language("fi")
    assert area2.post_office == "ESPOO"
    area2.set_current_language("sv")
    assert area2.post_office == "ESBO"
    area2.set_current_language("en")
    assert area2.post_office == "ESPOO"

    area3.refresh_from_db()
    area3.set_current_language("fi")
    assert area3.post_office == "ASKOLA"
    area3.set_current_language("sv")
    assert area3.post_office == "ASKOLA"
    area3.set_current_language("en")
    assert area3.post_office == "ASKOLA"


@mark.django_db
def test_import_post_offices_uses_finnish_fallback_for_swedish(tmp_path):
    """Test that Finnish is used as fallback when Swedish is missing."""
    area = PostalCodeAreaFactory(postal_code="00900")

    zip_file = tmp_path / "postal_codes.zip"
    create_test_zip(zip_file, [("00900", "HELSINKI", "")])
    call_command("import_post_offices", str(zip_file))

    area.refresh_from_db()
    area.set_current_language("fi")
    assert area.post_office == "HELSINKI"
    area.set_current_language("sv")
    assert area.post_office == "HELSINKI"


@mark.django_db
def test_import_post_offices_uses_swedish_fallback_for_finnish(tmp_path):
    """Test that Swedish is used as fallback when Finnish is missing."""
    area = PostalCodeAreaFactory(postal_code="00900")

    zip_file = tmp_path / "postal_codes.zip"
    create_test_zip(zip_file, [("00900", "", "HELSINGFORS")])
    call_command("import_post_offices", str(zip_file))

    area.refresh_from_db()
    area.set_current_language("fi")
    assert area.post_office == "HELSINGFORS"
    area.set_current_language("sv")
    assert area.post_office == "HELSINGFORS"


@mark.django_db
def test_import_post_offices_skips_missing_postal_codes(tmp_path):
    """Test that the command skips postal codes that don't exist in the database."""
    area = PostalCodeAreaFactory(postal_code="00900")

    zip_file = tmp_path / "postal_codes.zip"
    create_test_zip(
        zip_file,
        [
            ("00900", "HELSINKI", "HELSINGFORS"),
            ("99999", "NONEXISTENT", "EXISTERAR INTE"),
        ],
    )
    call_command("import_post_offices", str(zip_file))

    area.refresh_from_db()
    area.set_current_language("fi")
    assert area.post_office == "HELSINKI"

    assert not PostalCodeArea.objects.filter(postal_code="99999").exists()


@mark.django_db
def test_import_post_offices_handles_whitespace(tmp_path):
    """Test that the command properly handles whitespace in post office names."""
    area = PostalCodeAreaFactory(postal_code="00900")

    zip_file = tmp_path / "postal_codes.zip"
    create_test_zip(
        zip_file,
        [("00900", "HELSINKI                      ", "HELSINGFORS                   ")],
    )
    call_command("import_post_offices", str(zip_file))

    area.refresh_from_db()
    area.set_current_language("fi")
    assert area.post_office == "HELSINKI"
    area.set_current_language("sv")
    assert area.post_office == "HELSINGFORS"
