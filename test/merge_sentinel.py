import glob
import json
from collections import defaultdict
from osgeo import gdal
import os
import pandas as pd

files_to_mosaic = glob.glob(r'C:\Pycharm_Projects\GISTask\test\sentinel_output\sentinel_1_ortho\*\*\*.json')
output_path = r"C:\_data\sentinel\sentinel_1_ortho"
sentinel_type = "sentinel1_VV_decibel_gamma0"

geo_files = defaultdict(list)
for meta in files_to_mosaic:
    # Opening JSON file
    f = open(meta, )

    # returns JSON object as
    # a dictionary
    data = json.load(f)
    _from = data['payload']['input']['data'][0]['dataFilter']['timeRange']['from'].split('T')[0]
    _to = data['payload']['input']['data'][0]['dataFilter']['timeRange']['to'].split('T')[0]
    tif_file = meta.replace("request.json", "response.tiff")
    geo_files[f"{_from}_{_to}"].append(tif_file)

# merge data
for key, file_list in geo_files.items():
    df = pd.DataFrame({'date': [key.split("_")[0]]})
    year = key.split("-")[0]
    quarter = pd.to_datetime(df.date).dt.quarter.values[0]

    key_str = f"{year}-Q{quarter}"
    file_name = f"{key_str}_{sentinel_type}.tif"
    file_path = os.path.join(output_path, file_name)
    print(f"merge {file_name}")

    vrt_path = file_path.replace(".tif", ".vrt")
    vrt = gdal.BuildVRT(vrt_path, file_list)
    gdal_result = gdal.Translate(file_path, vrt, format='GTiff')
print("done...")

