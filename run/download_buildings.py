import osmnx as ox
import geopandas as gpd
import os
from helperFunctions.gen_functions import getargs
from shapely.geometry import Polygon

from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
import sys

QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.12\apps\qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Add the path to processing so we can import it next
sys.path.append(r'C:\Program Files\QGIS 3.12\apps\qgis\python\plugins')
# Imports usually should be at the top of a script but this unconventional
# order is necessary here because QGIS has to be initialized first
import processing
from processing.core.Processing import Processing

from qgis.gui import *
import qgis.utils
from qgis.utils import iface
import shutil
from qgis.PyQt import QtGui

Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
feedback = QgsProcessingFeedback()


def download_buildings(args):
    bbox = {'north': 47.109626, 'south': 47.003436, 'east': 15.506172, 'west': 15.370560}

    tags = {'building': True}
    buildings_file = os.path.join(args.output_path, "buildings.gpkg")

    print("create bounding box...")
    # gdf = gpd.read_file('D:/_task/building.gpkg')

    lat_point_list = [bbox['north'], bbox['south'], bbox['south'],  bbox['north']]
    lon_point_list = [bbox['west'], bbox['west'], bbox['east'],  bbox['east']]

    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    crs = {'init': 'epsg:4326'}
    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom]).to_crs("EPSG:3857")
    print(polygon.geometry)

    polygon.to_file(buildings_file, layer='bbox', driver="GPKG")
    print("done...")
    print()

    # specify that we're retrieving building footprint geometries an filter buildings which contain height values
    print("download osm data and prepare data set")
    gdf = ox.geometries_from_bbox(north=bbox['north'], south=bbox['south'], east=bbox['east'], west=bbox['west'],
                                  tags=tags)
    gdf = ox.project_gdf(gdf)
    gdf = gdf[gdf.height.notna()]

    # Just keep height attribute and transform to epsg: 3857
    gdf.drop(gdf.columns.difference(['unique_id', 'geometry', 'height']), 1, inplace=True)
    gdf = gdf.to_crs("EPSG:3857")
    gdf.to_file(buildings_file, layer='buildings', driver="GPKG")
    print("done...")
    print()

    # # convert height gpkg to raster with 5 X 5 m
    # processing.run("gdal:rasterize", {
    #     'INPUT': buildings_file,
    #     'FIELD': 'height', 'BURN': 0, 'UNITS': 1, 'WIDTH': 5, 'HEIGHT': 5,
    #     'EXTENT': '1711892.84785161,1724783.83412861,5943911.09088936,5959628.48513653 [EPSG:3857]', 'NODATA': 0,
    #     'OPTIONS': '', 'DATA_TYPE': 5, 'INIT': None, 'INVERT': False, 'EXTRA': '', 'OUTPUT': 'D:/__test888_slay.tif'})


if __name__ == "__main__":
    download_buildings(getargs())
