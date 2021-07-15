import rasterio
import os
import glob
from os.path import isfile, join
from os import listdir
from rasterio.merge import merge
from osgeo import gdal

file_path = "C:/_data/vexcel/windpark/_subsets/compressed"
merged_file = "C:/_data/vexcel/windpark/_subsets/compressed/merged.tif"

file_list = glob.glob(os.path.join(os.path.join(file_path, "*.tif")))

print("merge files")

vrt_path = merged_file.replace(".tif", ".vrt")
vrt = gdal.BuildVRT(vrt_path, file_list)
gdal_result = gdal.Translate(merged_file, vrt, format='GTiff')


# mosaic, out_trans = merge(file_list)
#
# # Copy the metadata
# out_meta = mosaic.meta.copy()
#
# # Update the metadata
# out_meta.update({"driver": "GTiff",
#                  "height": mosaic.shape[1],
#                  "width": mosaic.shape[2],
#                  "transform": out_trans
#                  }
# )
# # Write the mosaic raster to disk
# print(f"  write mosaic raster to disk...")
# with rasterio.open(merged_file, "w", **out_meta) as dest:
#     dest.write(mosaic)
