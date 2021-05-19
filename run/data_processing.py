from helperFunctions.gen_functions import getargs, create_path
from os import listdir
from os.path import isfile, join
import os
from collections import defaultdict
from osgeo import gdal
import shapely
import matplotlib.pyplot as plt
from osgeo import osr, ogr
import geopandas as gpd
import rasterio
import rasterio.mask


shapely.speedups.disable()


def data_processing(args):
    """Maskes remote sensing images based on OSM buildings

        :param args: arguments from argument parser
        :return:
        """

    red_green_blue = {'LE07': ['B1.TIF', 'B2.TIF', 'B3.TIF'], 'LC08': ['B2.TIF', 'B3.TIF', 'B4.TIF']}
    geo_files = [f for f in listdir(args.output_path) if isfile(join(args.output_path, f))]

    # create WGS84 Spatial Reference
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(3857)
    extent = [1711042.91240746, 5942634.93312008, 1726139.17119292, 5959986.21916383]

    # vector data
    drv = ogr.GetDriverByName('GPKG')
    # feature_ds = drv.CreateDataSource("{}/buildings.gpkg".format(args.output_path))
    gdb = drv.Open("{}/buildings.gpkg".format(args.output_path), 0)

    buildings = gpd.read_file("{}/buildings.gpkg".format(args.output_path), layer='buildings')
    src = rasterio.open("D:/PycharmProjects/GISTask/output/proj/LC08_L1TP_190027_20130618_20170503_01_T1_B3_proj.TIF")
    out_image, out_transform = rasterio.mask.mask(src, buildings.geometry, crop=True)
    out_meta = src.meta
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    with rasterio.open("RGB.byte.masked.tif", "w", **out_meta) as dest:
        dest.write(out_image)

    print()
    print("reproject raster to epsg:3857 and clip to bbox extend of aoi for files:")
    create_path(os.path.join(args.output_path, "proj"))
    composite_dict = defaultdict(list)
    for file in geo_files:
        if file.split("_")[-1] in red_green_blue.get(file.split("_")[0], []):
            in_file = os.path.join(args.output_path, file)
            ds = gdal.Open(in_file)
            out_file = os.path.join(args.output_path, 'proj', file.replace(".TIF", "_proj.TIF"))
            # array = ds.GetRasterBand(1).ReadAsArray()
            # plt.imshow(array)
            # plt.colorbar()
            # plt.show()
            # print(ds.GetGeoTransform())
            # print(ds.GetProjection())
            ds_reprojected = gdal.Warp(out_file, in_file, outputBounds=extent, outputBoundsSRS='EPSG:3857',
                                       dstSRS='EPSG:3857', xRes=5.0, yRes=5.0)
            print("  reprojected file stored to {}".format(out_file))
            # create dictionary for later creation of composite image
            composite_dict[file.split("_T1")[0]].append(ds_reprojected)

    # create composite image
    print("\ncreate composite image of r, g, b bands, mask files based on buildings layer and retile the masked images")
    rgb_order = [2, 1, 0]
    for mask_file in composite_dict:
        create_path(os.path.join(args.output_path, "composite"))
        composite_file = os.path.join(args.output_path, "composite", "{}.vrt".format(mask_file))
        vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic', addAlpha=False, separate=True)
        vrt_raster = gdal.BuildVRT(composite_file, [composite_dict[mask_file][i] for i in rgb_order], options=vrt_options)
        print("  virtual file stored to {}".format(composite_file))

        # create masked file based on building gpkg
        create_path(os.path.join(args.output_path, "mask"))
        out_file_mask = os.path.join(args.output_path, "mask", "{}.tif".format(mask_file))
        gdal.Warp(out_file_mask, vrt_raster,
                  cutlineDSName=buildings,
                  cropToCutline=True,
                  dstNodata=0)


if __name__ == "__main__":
    data_processing(args=getargs())
