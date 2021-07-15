from owslib.wms import WebMapService
from rasterio import MemoryFile, Affine
from rasterio.plot import show
import rasterio
from rasterio.warp import calculate_default_transform
import math
import numpy as np
import os
import sys
from osgeo import gdal, osr
import sys
from pathlib import Path


from helperFunctions.gen_functions import getargs, create_path


def download_wms(args):
    url = 'https://gis.stmk.gv.at/arcgis/services/OGD/ALSGelaendeinformation_1m_UTM33N/MapServer/WMSServer'
    # url = 'https://data.wien.gv.at/daten/geo?version=1.3.0'
    url = 'https://map.dfg.ca.gov/arcgis/services/Base_Remote_Sensing/NAIP_2020/ImageServer/WMSServer'
    wms = WebMapService(url)

    """
    https://gis.stmk.gv.at/arcgis/services/OGD/ALSGelaendeinformation_1m_UTM33N/MapServer/WMSServer?service
    =WMS&request=GetMap&version=1.3.0&BGCOLOR=0xFFFFFF&crs=
    EPSG:32633&bbox=
    515640.5190082641,
    5202075.827014463,
    551284.7214876037,
    5220046.445764463
    &layers=Gelaendehoehe_Gesamtmodell&width=1682&height=849&format=image/bmp
    """

    folder_path = r"C:\temp"
    BASE_PATH = r"C:\temp2"
    folder = Path(folder_path)

    l = []
    for f in folder.glob('**/*.tif'):
        f_path = f.as_posix()
        l.append(f_path)

    tile_files = [f for f in folder.glob('**/*.tif')]

    vrt_path = os.path.join(BASE_PATH, 'prov_vrt.vrt')
    vrt = gdal.BuildVRT(vrt_path, l)

    result = os.path.join(BASE_PATH, 'merged.tif')
    gdal.Translate(result, vrt, format='GTiff')


    print(list(wms.contents))
    print()
    print(wms.getOperationByName('GetMap').methods)
    print(wms.getOperationByName('GetMap').formatOptions)
    print()

    # Wien
    # x_min = 16.273974736842106
    # y_min = 48.237936798891965
    # x_max = 16.395343684210523
    # y_max = 48.31535741163435
    # size = (1427, 911)
    # crs = 'EPSG:4326'
    # layer = 'ogdwien:FLIESSGEWOGD'

    # Land Steiermark
    # x_min = 520490.8610143307
    # y_min = 5297719.1287194025
    # x_max = 520934.7048942241
    # y_max = 5298002.2543943655
    # size = (1427, 911)
    # layer = 'Gelaendehoehe_Gesamtmodell'
    # crs = 'EPSG:32633'

    # x_min = 517813.4903421879
    # y_min = 5224486.282982498
    # x_max = 530691.5979046926
    # y_max = 5232701.160017107
    # size = (1427, 911)
    # crs = 'EPSG:32633'
    # layer = 'Gelaendehoehe_Gesamtmodell'

    # print(wms[layer].styles)

    # NAIP
    # x_min = -13500339.576605948
    # y_min = 4390750.564719817
    # x_max = -13496384.22721686
    # y_max = 4392744.720036814
    # size = (1682, 849)
    # layer = '0'
    # crs = 'EPSG:3857'

    # bbox_area = (-13558322.745501576, 4472774.727182063, -13266994.935942067, 4641770.884737643)
    # bbox = (-13290102.003279826, 4507448.700980318, -13287994.787972087, 4508671.074123097)
    bbox_area = (-121.640253234, 37.557678957, -120.821346156, 37.952205699)
    bbox = (-121.640253234, 37.557678957, -120.821346156, 37.952205699)
    size = (1569, 911)
    layer = '0'
    crs = 'EPSG:3857'
    crs = 'EPSG:4326'

    width = abs(bbox[2] - bbox[0])
    height = abs(bbox[3] - bbox[1])

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(int(crs.split(":")[1]))

    i = 0
    for y_width in np.arange(bbox_area[1], bbox_area[3], height):
        for x_width in np.arange(bbox_area[0], bbox_area[2], width):
            subset_box = (x_width, y_width, x_width + width, y_width + height)

            print(subset_box)
            print(width, height)
            img = wms.getmap(
                layers=[layer],
                srs=crs,
                # bbox=bbox,
                bbox=subset_box,
                size=size,
                # size=(width, height),wid
                format='image/tiff'
            )

            # create transformation based on bounding box parameters
            # transform, transform_width, transform_height = calculate_default_transform(crs, crs, size[0], size[1],
            #                                                                            *subset_box)

            transform = rasterio.transform.from_bounds(*subset_box, size[0], size[1])

            with MemoryFile(img) as memfile:
                with memfile.open() as dataset:
                    # print(dataset.profile)
                    meta_data = dataset.meta.copy()
                    meta_data.update({
                        'crs': crs,
                        'transform': transform,
                        'width': dataset.meta['width'],
                        'height': dataset.meta['height']
                    })
                    show(dataset)
                    fn = 'C:/temp/new_raster.tif'
                    driver = gdal.GetDriverByName('GTiff')
                    data_array = dataset.read()
                    print(size[0], size[1])
                    ds = driver.Create(fn, xsize=size[0], ysize=size[1], bands=3, eType=gdal.GDT_Byte)
                    ds.GetRasterBand(1).WriteArray(data_array[0, :, :])
                    ds.GetRasterBand(2).WriteArray(data_array[1, :, :])
                    ds.GetRasterBand(3).WriteArray(data_array[2, :, :])

                    geot = (transform[2], transform[0], 0, transform[5], 0, transform[4])
                    ds.SetGeoTransform(geot)

                    ds.SetProjection(srs.ExportToWkt())
                    ds = None

                    path = os.path.join(args.output_path, 'wms')
                    create_path(os.path.join(args.output_path, 'wms'))
                    file = os.path.join(path, f"subset_{i}.tif")
                    with rasterio.open(file, 'w', **meta_data) as outds:
                        outds.write(dataset.read())

            i += 1


def download_wms_example():
    url = 'https://services.terrascope.be/wms/v2?'
    # url = 'https://gis.stmk.gv.at/arcgis/services/OGD/ALSGelaendeinformation_1m_UTM33N/MapServer/WMSServer'
    wms = WebMapService(url)

    print(list(wms.contents))

    x_min = 556945.9710290054
    y_min = 6657998.9149440415
    x_max = 575290.8578174476
    y_max = 6663655.255037144

    layer = 'CGS_S2_RADIOMETRY'

    # sys.exit(0)
    img = wms.getmap(
        layers=[layer],
        srs='EPSG:3857',
        bbox=(x_min, y_min, x_max, y_max),
        size=(1920, 592),
        format='image/png',
        time='2020-06-01'
    )

    with MemoryFile(img) as memfile:
        with memfile.open() as dataset:
            show(dataset)
            print(dataset.profile)


if __name__ == "__main__":
    # download_wms_example()
    download_wms(args=getargs())
    print()
