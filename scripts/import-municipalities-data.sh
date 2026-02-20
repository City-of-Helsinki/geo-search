#!/bin/sh

set -e

if [ $# -eq 0 ]
then
    echo "Municipality shapefile path required."
    echo ""
    echo "Usage: $0 <path-to-shapefile>"
    echo ""
    echo "Example:"
    echo "  $0 /tmp/nls/SuomenKuntajako_2026_10k.shp"
    echo ""
    echo "Download municipality data from:"
    echo "https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/datasets-and-interfaces/"
    echo "product-descriptions/division-administrative-areas-vector"
    echo ""
    echo "The data must be manually downloaded from NLS following their"
    echo "download process, then extracted from the ZIP file."
    exit 0
fi

SHAPEFILE_PATH="$1"

if [ ! -f "$SHAPEFILE_PATH" ]
then
    echo "Error: Shapefile not found: $SHAPEFILE_PATH" >&2
    exit 1
fi

echo "Importing municipalities from $SHAPEFILE_PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
python "$SCRIPT_DIR/../manage.py" import_municipalities "$SHAPEFILE_PATH"

echo "Municipality import complete!"
