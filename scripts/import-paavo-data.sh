#!/bin/bash

set -e

available_provinces="'uusimaa' and 'varsinais-suomi'"

if [ $# == 0 ]
then
    echo "No province argument supplied."    
    echo "Available provinces are ${available_provinces}."
    exit 0
fi

declare -A bbox
bbox["varsinais-suomi"]="125189.83,6611707.59,334187.32,6781558.98"
bbox["uusimaa"]="267392.57814054575,6636189.158504381,476288.57814054575,6747293.158504381"

if [ ${bbox[$1]+_} ] 
then 
    echo "Importing Paavo data for province $1."; 
else 
    echo "Province $1 not found, available provinces are ${available_provinces}."; 
    exit 0
fi

# URL to Paavo WFS service
DATA_URL="http://geo.stat.fi/geoserver/wfs?SERVICE=wfs&version=1.0.0&request=GetFeature&srsName=EPSG:3067&outputFormat=SHAPE-ZIP&typeNames=pno_meri_2021&bbox=${bbox[$1]}"

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