#!/bin/sh

set -e

# URL to a zip file containing .shp files
DATA_URL=https://aineistot.vayla.fi/digiroad/latest/Maakuntajako_DIGIROAD_R_EUREF-FIN/UUSIMAA.zip

# Directory where the data will be downloaded and extracted
DATA_DIR=/tmp/digiroad

# Pattern identifying the shapefiles (.dbf, .prj, .shp, .shx).
# The shapefiles are named DR_LINKKI.* or DR_LINKKI_K.*, depending
# on the dataset. This pattern is compatible with both.
SHAPEFILE_PATTERN="*/DR_LINKK*"

# The shapefiles will be extracted to this directory
EXTRACTED_DIR=$DATA_DIR/extracted

# The converted M removed shapefiles are saved in this directory
CONVERTED_DIR=$DATA_DIR/converted

# Download the source data
mkdir -p $DATA_DIR
#curl "$DATA_URL" -o $DATA_DIR/data.zip

# Extract the shapefiles from the archive
rm -rf $EXTRACTED_DIR
unzip $DATA_DIR/data.zip $SHAPEFILE_PATTERN -d $EXTRACTED_DIR

# Remove the measurements (M coordinate) from each shapefile.
# This is done because Django's OGRGeomType class doesn't support LineStringZM geometries:
# https://github.com/django/django/blob/ca9872905559026af82000e46cde6f7dedc897b6/django/contrib/gis/gdal/geomtype.py#L9
rm -rf $CONVERTED_DIR
mkdir -p $CONVERTED_DIR
shapefiles=$(find $EXTRACTED_DIR -type f -name "DR_LINKK*.shp")
for source_file in $shapefiles; do
  target_file=$(echo "$source_file" | sed "s:$EXTRACTED_DIR/:$CONVERTED_DIR/:")
  mkdir -p $(dirname $target_file)
  echo "Converting $source_file -> $target_file..."
  ogr2ogr -f "ESRI Shapefile" $target_file $source_file -dim XYZ
done

# Run the management command with all the shapefiles as arguments
SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
python "$SCRIPT_DIR/../manage.py" import_addresses $(find $CONVERTED_DIR -type f -name "DR_LINKK*.shp")