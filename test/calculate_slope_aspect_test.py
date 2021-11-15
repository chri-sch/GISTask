from osgeo import gdal
import rasterio
import richdem as rd

def calculate_slope(DEM):
    gdal.DEMProcessing('slope.tif', DEM, 'slope')
    # with rasterio.open('slope.tif') as dataset:
    #     slope = dataset.read(1)
    # return slope

calculate_slope(r'C:\_data\vexcel\orlando\dsm\orlando_dsm_10.tif')
