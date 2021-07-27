import rasterio
import os
import glob
from os.path import isfile, join
from os import listdir

file_path = r"C:\_data\vexcel\san_francisco\ortho"
output_path = r"C:\_data\vexcel\san_francisco\ortho"


file_list = glob.glob(os.path.join(os.path.join(file_path, "*.tif")))

# file_list = [r"C:\_data\vexcel\san_francisco\ortho\bluesky-ultra_san-francisco.tif"]
for file in file_list:
    with rasterio.open(file) as src:
        # Write an array as a raster band to a new 8-bit file. For
        # the new file's profile, we start with the profile of the source
        profile = src.profile

        # And then change the band count to 1, set the
        # dtype to uint8, and specify LZW compression.
        profile.update(
            # compress='deflate',
            count=3)

        out_file = os.path.join(output_path, "new" + (os.path.basename(file)))
        print(out_file)

        with rasterio.open(out_file, 'w', **profile) as dst:
            dst.write(src.read()[0:3, :, :])
