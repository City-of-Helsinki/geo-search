#!/bin/sh

set -e

echo "WARNING: This will delete all address data from the database!"
echo "This includes:"
echo "  - All addresses"
echo "  - All streets"
echo "  - All municipalities"
echo ""
echo "Press Ctrl+C to cancel, or press Enter to continue..."
read -r _

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
python "$SCRIPT_DIR/../manage.py" delete_address_data
