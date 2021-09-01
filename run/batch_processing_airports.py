import cv2
# import arcpy
import re
import string
# from arcpy import env
# from arcpy.sa import *
# import geopandas as gpd
# import grass.script as grass
# from grass.pygrass.vector import geometry
import numpy as np
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from glob import glob
import sys
import shutil

# arcpy.env.workspace = "D:\Input_images\SynthaaS_Aircraft"
in_imgpath = r'C:\Pycharm_Projects\GISTask\input\*.TIF'
print("Start processing...")
if __name__ == '__main__':
    for filename in glob(in_imgpath):
        # Open Raster...
        img = cv2.imread(filename, 3)
        path, base_filename = os.path.split(filename)
        dataset1 = gdal.Open(filename)
        # Get projection and transformation from original raster
        projection = dataset1.GetProjection()
        geotransform = dataset1.GetGeoTransform()

        # Export Edge Raster
        # Convert RGB image to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian filter to reduce the noise (Smoothing images)
        blur = cv2.GaussianBlur(gray_img, (5, 5), 0)
        # Apply Canny Filter to detect edges
        edges = cv2.Canny(blur, 100, 255, 3, L2gradient=True)
        print("Processing completed for {}".format(base_filename))

        # write edges new
        out_imgpath = os.path.join(path, "Edges_" + base_filename)
        driver = gdal.GetDriverByName('GTiff')
        ds = driver.Create(out_imgpath,
                           edges.shape[1],
                           edges.shape[0],
                           bands=1,
                           eType=gdal.GDT_Byte)
        ds.GetRasterBand(1).WriteArray(edges)
        ds.SetGeoTransform(geotransform)
        ds.SetProjection(projection)

        #  create output datasource
        dst_layername = "poligonized_shp"
        drv = ogr.GetDriverByName("ESRI Shapefile")
        dst_ds = drv.CreateDataSource(dst_layername + ".shp")
        dst_layer = dst_ds.CreateLayer(dst_layername, srs=None)

        gdal.Polygonize(edges, None, dst_layer, -1, [], callback=None)
        dst_ds.Destroy()

        polygon_response(raster, poligonized_shp)

        #  create output datasource


        ds = None
        sys.exit(0)

        path2, base_filename2 = os.path.split(out_imgpath)
        cv2.imwrite(out_imgpath, edges)
        filename_ext = os.path.splitext(base_filename2)[0]
        print("Edges raster named {} saved.".format(out_imgpath))

        # Assign Projection And Transformation To Edge Raster
        dataset2 = gdal.Open(out_imgpath, gdal.GA_Update)
        dataset2.SetGeoTransform(geotransform)
        dataset2.SetProjection(projection)
        print("Projection for {} set.".format(out_imgpath))
        # Convert Edge Raster To Polyline
        projection_out = dataset2.GetProjection()
        geotransform_out = dataset2.GetGeoTransform()

        print(projection_out)
        print(geotransform_out)
        out_layername = os.path.join(path, "Lines_" + filename_ext + ".shp")
        # arcpy.conversion.RasterToPolyline(out_imgpath, out_layername, "ZERO", 0, "SIMPLIFY", "Value")