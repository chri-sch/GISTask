import rasterio
import os
import glob
from osgeo import gdal
from os.path import isfile, join
from os import listdir

file_path = r"C:\temp"
output_path = r"C:\temp"


file_list = glob.glob(os.path.join(os.path.join(file_path, "*.tif")))

# file_list = [r"C:\_data\vexcel\san_francisco\ortho\bluesky-ultra_san-francisco.tif"]
for file in file_list:
    with rasterio.open(file) as src:
        # Write an array as a raster band to a new 8-bit file. For
        # the new file's profile, we start with the profile of the source
        profile = src.profile

        # And then change the band count to 1, set the
        # dtype to uint8, and specify LZW compression.
        profile.update(compress='deflate')

        out_file = os.path.join(output_path, "_" + (os.path.basename(file)))
        print(out_file)

        with rasterio.open(out_file, 'w', **profile, BIGTIFF='YES') as dst:
            dst.write(src.read())
    os.remove(file)
    print(f"  file {file} removed")


base_path = r"C:\temp"
file_name = r"C:\temp\orlando_first_row_merge.tif"

search_criteria = "*.tif"
q = os.path.join(base_path, search_criteria)
files = glob.glob(q)

print(file_name)
vrt_path = file_name.replace(".tif", ".vrt")
vrt = gdal.BuildVRT(vrt_path, files)
gdal_result = gdal.Translate(file_name, vrt, format='GTiff')
print("done...")
