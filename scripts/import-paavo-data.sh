#!/bin/sh

set -e

# URL to Paavo WFS service
DATA_URL="http://geo.stat.fi/geoserver/wfs?SERVICE=wfs&version=1.0.0&request=GetFeature&srsName=EPSG:3067&outputFormat=SHAPE-ZIP&typeNames=pno_meri_2021&bbox=267392.57814054575,6636189.158504381,476288.57814054575,6747293.158504381"

# Directory where the data will be downloaded and extracted
DATA_DIR=/tmp/paavo

# The shapefiles will be extracted to this directory
EXTRACTED_DIR=$DATA_DIR/extracted

# Download the source data
mkdir -p $DATA_DIR
curl "$DATA_URL" -o $DATA_DIR/data.zip

# Extract the files from the archive
rm -rf $EXTRACTED_DIR
unzip $DATA_DIR/data.zip -d $EXTRACTED_DIR

# Run the management command with all the shapefiles as arguments
SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
python "$SCRIPT_DIR/../manage.py" import_postal_codes $(find $EXTRACTED_DIR -type f -name "*.shp")
