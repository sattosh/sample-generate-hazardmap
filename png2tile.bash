#!/bin/bash

# This script converts a PNG image to a tileset.
gdal_translate -of GTiff -a_ullr 1646.3710000024314 -113962.59399999422 73116.37100000243 -233982.59399999422 -a_srs EPSG:2452 dist/output.png dist/georeferenced.tif
gdalwarp -of GTiff -t_srs EPSG:3857 dist/georeferenced.tif dist/reprojected.tif
gdal2tiles.py dist/reprojected.tif tiles -z4-13 --xyz --processes=4 