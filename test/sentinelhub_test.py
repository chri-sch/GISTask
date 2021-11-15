from sentinelhub import SHConfig

import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import sys
import datetime as dt
import pandas as pd
from datetime import datetime, timedelta
from settings.sentinel import evalscript_all_bands, eval_script_sentinel_1

from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, SentinelHubDownloadClient, \
    DataCollection, bbox_to_dimensions, DownloadRequest, SentinelHubCatalog, filter_times
from sentinelhub import SentinelHubRequest, BBoxSplitter

# create quarterly date time arrays
# date_array = np.arange(datetime(2017, 1, 1), datetime(2021, 1, 1), timedelta(months=1)).astype(datetime)

# read aoi
gdf = gpd.read_file(r"C:\_data\vector\sentinel\aoi_utm.gpkg", layer="aoi_utm")
# gdf = gpd.read_file(r"C:\_data\vector\sentinel\mead.geojson")

config = SHConfig()

# config.instance_id = '541703c6-ea75-4a7c-8062-a23810ca9a0e'
config.sh_client_id = '4357d203-b954-4d8e-9f0b-655c4601fe6f'
config.sh_client_secret = 'ar)3BfZ3B}Gt.?)WSH0AwL35XeKoM8C0>OAcKfrR'
config.save()

if not config.sh_client_id or not config.sh_client_secret:
    print("Warning! To use Process API, please provide the credentials (OAuth client ID and client secret).")




"""
 collection
"""
catalog = SentinelHubCatalog(config=config)

catalog.get_info()
collections = catalog.get_collections()

resolution = 10
bbox = [gdf.geometry.bounds.minx.values[0],
        gdf.geometry.bounds.miny.values[0],
        gdf.geometry.bounds.maxx.values[0],
        gdf.geometry.bounds.maxy.values[0]]
mead_bbox = BBox(bbox=bbox, crs=CRS.UTM_11N)

boxes = BBoxSplitter([gdf.geometry[0]], crs=CRS.UTM_11N, split_shape=(4, 3))

time_interval = '2017-01-01', '2018-12-31'

# split boxes
# BBoxSplitter([gdf.geometry[0]], crs=CRS.UTM_11N, split_shape=(4, 3))

search_iterator = catalog.search(
    DataCollection.SENTINEL2_L1C,
    bbox=mead_bbox,
    time=time_interval,
)

# search_iterator = catalog.search(
#     DataCollection.SENTINEL1,
#     bbox=mead_bbox,
#     time=time_interval,
#     query={
#         "eo:cloud_cover": {
#             "lt": 5
#         }
#     },
#     fields={
#         "include": [
#             "id",
#             "properties.datetime",
#             "properties.eo:cloud_cover"
#         ],
#         "exclude": []
#     }
#
# )

results = list(search_iterator)
print('Total number of results:', len(results))
print()
# Combine Catalog API with Process API
time_difference = dt.timedelta(hours=1)
all_timestamps = search_iterator.get_timestamps()
unique_acquisitions = filter_times(all_timestamps, time_difference)

# converte date time to
df = pd.DataFrame(unique_acquisitions, columns=["date_time"])

# iterate through boxes
process_requests = []
i = 0
for box in boxes.bbox_list[0:2]:
    box_size = bbox_to_dimensions(box, resolution=resolution)
    n = 0
    for attr, group in df.groupby([df.date_time.dt.year, df.date_time.dt.quarter]):
        print(f"find data between {group.values[0][0]} and {group.values[-1][0]}")

        request_all_bands = SentinelHubRequest(
            data_folder=f'sentinel_output/SENTINELtest/box_{i}',
            evalscript=evalscript_all_bands,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L1C,
                    time_interval=(group.values[0][0], group.values[-1][0]),
                    # other_args={"polarization": "VV", "orthorectify": True, "demInstance": "COPERNICUS"}
                    mosaicking_order='leastCC',
                    maxcc=0.5
                )],
            responses=[
                SentinelHubRequest.output_response('default', MimeType.TIFF)
            ],
            bbox=box,
            size=box_size,
            config=config
        )
        n += 1
        process_requests.append(request_all_bands)

        # all_bands_img = request_all_bands.get_data(save_data=True)
        # for folder, _, filenames in os.walk(request_all_bands.data_folder):
        #     for filename in filenames:
        #         print(os.path.join(folder, filename))

        # if n >= 2:
        #     client = SentinelHubDownloadClient(config=config)
        #     download_requests = [request.download_list[0] for request in process_requests]
        #     data = client.download(download_requests)
        #     print()

    i += 1


client = SentinelHubDownloadClient(config=config)
download_requests = [request.download_list[0] for request in process_requests]
data = client.download(download_requests)
