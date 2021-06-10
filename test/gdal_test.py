from osgeo import gdal

import numpy as np

fn = 'C:/temp/new_raster.tif'

rasterband = np.zeros((10, 10))
rasterband2 = np.ones((10, 10))

driver = gdal.GetDriverByName('GTiff')
ds = driver.Create(fn, xsize=10, ysize=10, bands=2, eType=gdal.GDT_Float32)
ds.GetRasterBand(1).WriteArray(rasterband)
ds.GetRasterBand(2).WriteArray(rasterband2)
print('done')

