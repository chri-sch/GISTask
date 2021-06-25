import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from os import listdir
from os.path import isfile, join
import os

edited_path = "D:/PycharmProjects/GISTask/input/edited"
raw_data_path = "D:/PycharmProjects/GISTask/input/raw_data"
proj_path = "D:/PycharmProjects/GISTask/output/_proj_path"

geo_files = [f for f in listdir(edited_path) if isfile(join(edited_path, f))]

for f in geo_files:
    file_name = os.path.basename(f)

    with rasterio.open(os.path.join(raw_data_path, file_name)) as src_params:
        kwargs = src_params.meta.copy()
        kwargs['count'] = 3
        with rasterio.open(
            os.path.join(edited_path, file_name)) as src:
            with rasterio.open(os.path.join(proj_path, file_name), 'w', **kwargs) as dst:
                dst.write(src.read())
