import numpy as np
import matplotlib.pyplot as plt
import os, glob
from timeit import default_timer as timer
from osgeo import gdal

# Ortho_bluesky-ultra_21_359855_836952_60
files_to_mosaic = glob.glob(r'C:\temp\3\aoi_1\*.tif')

start = timer()
# files_to_mosaic = ["a.tif", "b.tif"] # However many you want.
g = gdal.Warp("output2.tif", files_to_mosaic, format="GTiff",
              options=["COMPRESS=DEFLATE", "NUM_THREADS=ALL_CPUS"]) # if you want , "NUM_THREADS=ALL_CPUS"
g = None # Close file and flush to disk

end = timer()
print("elapsed time:", end - start)

