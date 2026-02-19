#!/bin/sh

set -e

echo "Importing Posti post office data"

# Posti's postal code file URL
# The URL follows the format: https://www.posti.fi/webpcode/PCF_YYYYMMDD.zip
# where YYYYMMDD is the date. You can find the latest file at:
# https://www.posti.fi/webpcode/

# Get today's date in YYYYMMDD format
DATE=$(date +%Y%m%d)
DATA_URL="https://www.posti.fi/webpcode/PCF_${DATE}.zip"

DATA_DIR=/tmp/posti

# Download the source data
mkdir -p $DATA_DIR
echo "Downloading postal code data from Posti..."
curl --proto "=https" --tlsv1.2 -sSf -L -o $DATA_DIR/postal_codes.zip "$DATA_URL"

# Run the management command
SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
python "$SCRIPT_DIR/../manage.py" import_post_offices "$DATA_DIR/postal_codes.zip"

echo "Post office data import complete!"
