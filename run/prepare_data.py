import sys

from os import listdir
from os.path import isfile, join
from helperFunctions.gen_functions import getargs
import gdal

from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
import os
import geopandas as gpd
from collections import defaultdict

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

args = getargs()

# get arguments from argument parser

red_green_blue = ['B2.TIF', 'B3.TIF', 'B4.TIF']

# Add the path to processing so we can import it next
sys.path.append(r'C:\Program Files\QGIS 3.12\apps\qgis\python\plugins')
# Imports usually should be at the top of a script but this unconventional
# order is necessary here because QGIS has to be initialized first
import processing
from processing.core.Processing import Processing

geo_files = [f for f in listdir(args.output_path) if isfile(join(args.output_path, f))]

print("reproject raster to epsg:3857 and clip to bbox extend of aoi for files:")
composite_dict = defaultdict(list)
for file in geo_files:
    if file.split("_")[-1] in red_green_blue:
        out_file = os.path.join(args.output_path, 'proj', file.replace(".TIF", "_proj.TIF"))
        processing.run("gdal:warpreproject", {
            'INPUT': os.path.join(args.output_path, file),
            'SOURCE_CRS': QgsCoordinateReferenceSystem('EPSG:32633'),
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:3857'), 'RESAMPLING': 1, 'NODATA': None,
            'TARGET_RESOLUTION': 5, 'OPTIONS': '', 'DATA_TYPE': 0,
            'TARGET_EXTENT': '1711042.91240746,1726139.17119292,5942634.93312008,5959986.21916383 [EPSG:3857]',
            'TARGET_EXTENT_CRS': None, 'MULTITHREADING': False, 'EXTRA': '',
            'OUTPUT': out_file})
        print("reprojected file stored to {}".format(out_file))

        # create masked file based on building gpkg
        out_file_mask = os.path.join(args.output_path, "mask", file.replace(".TIF", "_mask.TIF"))
        processing.run("gdal:cliprasterbymasklayer", {
            'INPUT': out_file,
            'MASK': 'D:/Projekte_PV/chsc/PycharmProjects/TaskProject/run/output/buildings.gpkg|layername=buildings',
            'SOURCE_CRS': None, 'TARGET_CRS': None, 'NODATA': -99, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True,
            'KEEP_RESOLUTION': False, 'SET_RESOLUTION': False, 'X_RESOLUTION': None, 'Y_RESOLUTION': None,
            'MULTITHREADING': False, 'OPTIONS': '', 'DATA_TYPE': 0, 'EXTRA': '', 'OUTPUT': out_file_mask})
        print("masked file stored to {}".format(out_file_mask))

        # create dictionary for later creation of composite image
        composite_dict[file.split("_T1")[0]].append(out_file_mask)
print()

# create composite image
print("create composite image of r, g, b bands")
rgb_order = [2, 1, 0]
for mask_file in composite_dict:
    composite_file = os.path.join(args.output_path, "composite", "{}.TIF".format(mask_file))
    processing.run("gdal:buildvirtualraster", {'INPUT': [composite_dict[mask_file][i] for i in rgb_order],
                                               'RESOLUTION': 0, 'SEPARATE': True, 'PROJ_DIFFERENCE': False,
                                               'ADD_ALPHA': False, 'ASSIGN_CRS': None, 'RESAMPLING': 0,
                                               'SRC_NODATA': '',
                                               'EXTRA': '', 'OUTPUT': composite_file})
    print("composite file stored to {}".format(composite_file))

    tile_folder = os.path.join(args.output_path, "tiles", mask_file)
    if not os.path.exists(tile_folder):
        os.makedirs(tile_folder)

    processing.run("gdal:retile", {'INPUT': [composite_file],
                                   'TILE_SIZE_X': 512, 'TILE_SIZE_Y': 512, 'OVERLAP': 0, 'LEVELS': 1,
                                   'SOURCE_CRS': None, 'RESAMPLING': 0, 'DELIMITER': ';', 'OPTIONS': '', 'EXTRA': '',
                                   'DATA_TYPE': 2, 'ONLY_PYRAMIDS': False, 'DIR_FOR_ROW': False,
                                   'OUTPUT': tile_folder})

    # for tile_file in [f for f in listdir(tile_folder) if isfile(join(tile_folder, f))]:
    #     if tile_file.endswith('.tif'):
    #         processing.run("gdal:translate", {
    #             'INPUT': os.path.join(tile_folder, tile_file),
    #             'TARGET_CRS': None, 'NODATA': None, 'COPY_SUBDATASETS': False, 'OPTIONS': '', 'EXTRA': '',
    #             'DATA_TYPE': 0,
    #             'OUTPUT': os.path.join(tile_folder, tile_file.replace("tif", "jpg"))})

    for tile_file in [f for f in listdir(tile_folder) if isfile(join(tile_folder, f))]:
        if tile_file.endswith('.tif'):
            src_ds = gdal.Open(os.path.join(tile_folder, tile_file))

            # Open output format driver, see gdal_translate --formats for list
            format = "JP2OpenJPEG"
            driver = gdal.GetDriverByName(format)
            dst_ds = driver.CreateCopy(os.path.join(tile_folder, tile_file.replace("tif", "jpg")), src_ds)
            dst_ds = None
            src_ds = None


print("done..")
