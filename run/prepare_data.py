import sys

from os import listdir
from os.path import isfile, join
from helperFunctions.gen_functions import getargs, create_path

from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
import os
from collections import defaultdict

QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.12\apps\qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Add the path to processing so we can import it next
sys.path.append(r'C:\Program Files\QGIS 3.12\apps\qgis\python\plugins')
# Imports usually should be at the top of a script but this unconventional
# order is necessary here because QGIS has to be initialized first
from processing.core.Processing import Processing

Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
feedback = QgsProcessingFeedback()
# Add the path to processing so we can import it next
sys.path.append(r'C:\Program Files\QGIS 3.12\apps\qgis\python\plugins')

# Imports usually should be at the top of a script but this unconventional
# order is necessary here because QGIS has to be initialized first
import processing


def prepare_data(args):
    """Maskes remote sensing images based on OSM buildings

    :param args: arguments from argument parser
    :return:
    """

    red_green_blue = {'LE07': ['B1.TIF', 'B2.TIF', 'B3.TIF'], 'LC08': ['B2.TIF', 'B3.TIF', 'B4.TIF']}
    geo_files = [f for f in listdir(args.output_path) if isfile(join(args.output_path, f))]

    print()
    print("reproject raster to epsg:3857 and clip to bbox extend of aoi for files:")
    create_path(os.path.join(args.output_path, "proj"))
    composite_dict = defaultdict(list)
    for file in geo_files:
        if file.split("_")[-1] in red_green_blue.get(file.split("_")[0], []):
            out_file = os.path.join(args.output_path, 'proj', file.replace(".TIF", "_proj.TIF"))
            processing.run("gdal:warpreproject", {
                'INPUT': os.path.join(args.output_path, file),
                'SOURCE_CRS': QgsCoordinateReferenceSystem('EPSG:32633'),
                'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:3857'), 'RESAMPLING': 0, 'NODATA': None,
                'TARGET_RESOLUTION': 5, 'OPTIONS': '', 'DATA_TYPE': 0,
                'TARGET_EXTENT': '1711042.91240746,1726139.17119292,5942634.93312008,5959986.21916383 [EPSG:3857]',
                'TARGET_EXTENT_CRS': None, 'MULTITHREADING': False, 'EXTRA': '',
                'OUTPUT': out_file})
            print("  reprojected file stored to {}".format(out_file))

            # create dictionary for later creation of composite image
            composite_dict[file.split("_T1")[0]].append(out_file)
    print()

    # create composite image
    print("create composite image of r, g, b bands, mask files based on buildings layer and retile the masked images")
    rgb_order = [2, 1, 0]
    for mask_file in composite_dict:

        create_path(os.path.join(args.output_path, "composite"))
        composite_file = os.path.join(args.output_path, "composite", "{}.TIF".format(mask_file))
        virtualr = processing.run("gdal:buildvirtualraster", {'INPUT': [composite_dict[mask_file][i] for i in rgb_order],
                                                              'RESOLUTION': 0, 'SEPARATE': True, 'PROJ_DIFFERENCE': False,
                                                              'ADD_ALPHA': False, 'ASSIGN_CRS': None, 'RESAMPLING': 0,
                                                              'SRC_NODATA': '',
                                                              'EXTRA': '', 'OUTPUT': 'TEMPORARY_OUTPUT'})
        print("  composite file stored to {}".format(composite_file))

        processing.run("gdal:translate", {
            'INPUT': virtualr['OUTPUT'],
            'TARGET_CRS': None, 'NODATA': None, 'COPY_SUBDATASETS': False, 'OPTIONS': '', 'EXTRA': '', 'DATA_TYPE': 0,
            'OUTPUT': composite_file})

        # create masked file based on building gpkg
        create_path(os.path.join(args.output_path, "mask"))
        out_file_mask = os.path.join(args.output_path, "mask", "{}.tif".format(mask_file))
        processing.run("gdal:cliprasterbymasklayer", {
            'INPUT': composite_file,
            'MASK': "{}/buildings.gpkg|layername=buildings".format(args.output_path),
            'SOURCE_CRS': None, 'TARGET_CRS': None, 'NODATA': None, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True,
            'KEEP_RESOLUTION': False, 'SET_RESOLUTION': False, 'X_RESOLUTION': None, 'Y_RESOLUTION': None,
            'MULTITHREADING': False, 'OPTIONS': '', 'DATA_TYPE': 0, 'EXTRA': '', 'OUTPUT': out_file_mask})
        print("  masked file stored to {}".format(out_file_mask))

        # retile masked image
        tile_folder = os.path.join(args.output_path, "tiles", mask_file)
        create_path(tile_folder)
        processing.run("gdal:retile", {'INPUT': [out_file_mask],
                                       'TILE_SIZE_X': 512, 'TILE_SIZE_Y': 512, 'OVERLAP': 0, 'LEVELS': 1,
                                       'SOURCE_CRS': None, 'RESAMPLING': 0, 'DELIMITER': ';', 'OPTIONS': '', 'EXTRA': '',
                                       'DATA_TYPE': 0, 'ONLY_PYRAMIDS': False, 'DIR_FOR_ROW': False,
                                       'OUTPUT': tile_folder})

        tile_folder_jpg = os.path.join(args.output_path, "tiles", mask_file, "_JPG")
        create_path(tile_folder_jpg)
        # convert data in jpg format
        for tile_file in [f for f in listdir(tile_folder) if isfile(join(tile_folder, f))]:
            if tile_file.endswith('.tif'):
                processing.run("gdal:translate", {
                    'INPUT': os.path.join(tile_folder, tile_file),
                    'TARGET_CRS': None, 'NODATA': None, 'COPY_SUBDATASETS': False, 'OPTIONS': '', 'EXTRA': '',
                    'DATA_TYPE': 0,
                    'OUTPUT': os.path.join(tile_folder, "_JPG", tile_file.replace("tif", "jpg"))})
        print("  tiled files stored to {}".format(tile_folder))

    print("done..")


if __name__ == "__main__":
    prepare_data(args=getargs())
