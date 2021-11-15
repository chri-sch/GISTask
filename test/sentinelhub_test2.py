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

resolution = 10
bbox = [gdf.geometry.bounds.minx.values[0],
        gdf.geometry.bounds.miny.values[0],
        gdf.geometry.bounds.maxx.values[0],
        gdf.geometry.bounds.maxy.values[0]]
mead_bbox = BBox(bbox=bbox, crs=CRS.UTM_11N)

boxes = BBoxSplitter([gdf.geometry[0]], crs=CRS.UTM_11N, split_shape=(4, 3))
bbox = boxes.bbox_list[0]

catalog = SentinelHubCatalog(config=config)
catalog.get_info()
time_interval = '2015-01-01', '2021-12-31'
collections = catalog.get_collections()
search_iterator = catalog.search(
    DataCollection.SENTINEL1,
    bbox=mead_bbox,
    time=time_interval,
)
results = list(search_iterator)
print('Total number of results:', len(results))
print()
# Combine Catalog API with Process API
time_difference = dt.timedelta(hours=1)
all_timestamps = search_iterator.get_timestamps()
unique_acquisitions = filter_times(all_timestamps, time_difference)

# convert date time to
df = pd.DataFrame(unique_acquisitions, columns=["date_time"])

box_size = bbox_to_dimensions(bbox, resolution=resolution)

evalscript_all_bands = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["VV"],
            }],
            output: {
                id: "default",
                bands: 1,
                sampleType: "AUTO"
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.VV];
    }
"""
process_requests = []
i = 0

fill_times = ['2017-04-10_4', '2016-07-02_2', '2017-10-07_7']

for box in boxes.bbox_list:
    for attr, group in df.groupby([df.date_time.dt.year, df.date_time.dt.quarter]):
        box_size = bbox_to_dimensions(box, resolution=resolution)

        fill_str = F"{group.values[0][0].strftime('%Y-%m-%d')}_{i}"
        if fill_str in fill_times:
            print(f"box_{i}: find data between {group.values[0][0]} and {group.values[-1][0]}\n")
            request_all_bands = SentinelHubRequest(
                data_folder=f'sentinel_output/sentinel_1_ortho/box_{i}',
                evalscript=evalscript_all_bands,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL1,
                        time_interval=(group.values[0][0], group.values[-1][0]),
                        other_args={"polarization": "VV", "orthorectify": True, "demInstance": "COPERNICUS"}
                )],
                responses=[
                    SentinelHubRequest.output_response('default', MimeType.TIFF)
                ],
                bbox=box,
                size=box_size,
                config=config
            )

            # all_bands_img = request_all_bands.get_data(save_data=True)
            process_requests.append(request_all_bands)

    i += 1

client = SentinelHubDownloadClient(config=config)
download_requests = [request.download_list[0] for request in process_requests]
data = client.download(download_requests)
