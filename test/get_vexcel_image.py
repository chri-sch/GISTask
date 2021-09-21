import math
import threading

import rasterio as rasterio
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import concurrent.futures
import numpy as np
import json
import sys
import os
from datetime import datetime
from PIL import Image
import geopandas as gpd
from io import BytesIO
import tqdm
from pyproj import Transformer, Proj, transform, CRS
from affine import Affine

from shapely.geometry import box
from decimal import Decimal
import cv2
from typing import List
import boto3

class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()
class VexcelImages:
    def __init__(self, login_url, username, password):
        """Access Vexcel Images portal."""
        self.url = login_url

        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[600, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        self._expiration_date = None
        self._user = username
        self._pwd = password
        self.tile_extents: List[float] = []
        self.epsg: str = ""
        self.tile_count_x: int = 0
        self.tile_count_y: int = 0
        self.login(username=username, password=password)
        self.file_path = []

    def login(self, username, password):
        """Get an API key.

        Parameters
        ----------
        username : str
            Vexcel images username.
        password : str
            Vexcel images password.
        """

        payload = {'username': username, 'password': password}
        request_result = self.session.post(self.url, data=payload)

        if request_result.status_code != 200:
            sys.exit(f"Failed to login, response code: {request_result.status_code}")
        else:
            self.session.headers["X-Auth-Token"] = request_result.json().get('token')
            self._expiration_date = datetime.strptime(request_result.json().get('expiration_date'),
                                                      '%Y-%m-%dT%H:%M:%S')

    def request_image_slice(self, polygon, epsg, dim, zoom, layer="bluesky - ultra"):

        for wkt_idx, wkt_polygon in polygon.items():
            pass

        extract_url = f"https://api.gic.org/images/ExtractOrthoImages?zoom=" \
                      f"{zoom}&layer={layer}&epsg={epsg}&wkt={wkt_polygon}"
        with self.session.get(
                extract_url, stream=True, allow_redirects=True
        ) as r:

            if r.status_code != 200:
                sys.exit("Couldn't receive the image")
            elif 'image' in r.headers['Content-Type']:
                data_array = np.asarray(Image.open(BytesIO(r.content)))
        data_array = cv2.resize(data_array, (dim, dim), interpolation=cv2.INTER_AREA)
        print(wkt_idx, data_array.shape)
        return data_array

    @staticmethod
    def get_wkt(xmin, ymin, xmax, ymax):
        return box(xmin, ymin, xmax, ymax)

    @staticmethod
    def image_padding_axis_0(image, size):
        if image.shape[0] == size:
            return image
        image = np.append(image,
                          np.zeros((size - image.shape[0], image.shape[1], image.shape[2]), dtype=np.uint8),
                          axis=0)
        return image

    @staticmethod
    def image_padding_axis_1(image, size):
        if image.shape[1] == size:
            return image
        image = np.append(image,
                          np.zeros((image.shape[0], size - image.shape[1], image.shape[2]), dtype=np.uint8),
                          axis=1)
        return image

    def get_tiled_bounding_box_wkt(self, bbox, from_crs, to_crs, tile_size=200):
        self.epsg = to_crs
        tile_count = 0
        start_lon = bbox[0]
        start_lat = bbox[1]
        stop_lon = bbox[2]
        stop_lat = bbox[3]
        transformer = Transformer.from_crs(crs_from=from_crs, crs_to=to_crs)
        extent_osm = transformer.itransform([[start_lat, start_lon], [stop_lat, stop_lon]], switch=False)
        ex_list = []
        for coordinates in extent_osm:
            for point in coordinates:
                ex_list.append(point)
        scene_width = math.ceil(ex_list[2] - ex_list[0])
        scene_height = math.ceil(ex_list[3] - ex_list[1])
        self.tile_extents = [ex_list[0], ex_list[3]]
        self.tile_count_x = (scene_width // tile_size) + 1
        self.tile_count_y = (scene_height // tile_size) + 1
        tile_polygons = []
        for idx_y in range((scene_height // tile_size)):
            y_min = ex_list[3] - (idx_y * tile_size)
            y_max = ex_list[3] - ((idx_y + 1) * tile_size)
            for idx_x in range((scene_width // tile_size)):
                x_min = ex_list[0] + (idx_x * tile_size)
                x_max = ex_list[0] + ((idx_x + 1) * tile_size)
                x_min = float(Decimal(f"{x_min:.5f}" + "0001"))
                x_max = float(Decimal(f"{x_max:.5f}" + "0001"))
                y_min = float(Decimal(f"{y_min:.5f}" + "0001"))
                y_max = float(Decimal(f"{y_max:.5f}" + "0001"))
                wkt_polygon = self.get_wkt(x_min, y_min, x_max, y_max)
                tile_polygons.append({tile_count: wkt_polygon})
                tile_count += 1
            tile_polygons.append({tile_count: self.get_wkt(ex_list[0] + ((scene_width // tile_size) * tile_size),
                                                           y_min,
                                                           ex_list[2],
                                                           y_max)})
            tile_count += 1

        y_min = ex_list[3] - ((scene_height // tile_size) * tile_size)
        y_max = ex_list[1]
        for idx_x in range((scene_width // tile_size)):
            x_min = ex_list[0] + (idx_x * tile_size)
            x_max = ex_list[0] + ((idx_x + 1) * tile_size)
            tile_polygons.append({tile_count: self.get_wkt(x_min, y_min, x_max, y_max)})
            tile_count += 1
        tile_polygons.append({tile_count: self.get_wkt(ex_list[0] + ((scene_width // tile_size) * tile_size),
                                                       y_min,
                                                       ex_list[2],
                                                       y_max)})
        tile_count += 1

        return tile_polygons

    def get_ortho_image_tiles(self,
                              output_dir,
                              polygons,
                              zoom,
                              img_size,
                              tile_index,
                              layer_type="bluesky-ultra"
                              ):
        num_tiles = 2
        tile_index = tile_index.split('-')[-1]
        num_threads = os.cpu_count() - 1
        print(num_threads)
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            future = [executor.submit(self.request_image_slice,
                                      poly,
                                      self.epsg,
                                      img_size,
                                      zoom,
                                      layer_type) for poly in polygons]

        tile_count = 0

        for tile_iter in range(num_tiles):
            self.tile_extents[1] += tile_iter * -0.149 * img_size * self.tile_count_y//num_tiles
            for y_idx in range((tile_iter * self.tile_count_y//num_tiles),
                               self.tile_count_y//num_tiles + (tile_iter * self.tile_count_y//num_tiles), 1):
                for x_idx in range(self.tile_count_x):
                    if x_idx == 0:
                        tile = future[tile_count].result()
                        tile_count += 1
                    else:
                        tile = np.append(tile, future[tile_count].result(), axis=1)
                        tile_count += 1
                if y_idx == (tile_iter * self.tile_count_y//num_tiles):
                    big_image = tile
                else:
                    big_image = np.append(big_image, tile, axis=0)
                    del tile

            meta_data = dict()
            meta_data.update(
                {
                    "driver": "GTiff",
                    "bigtiff": "YES",
                    "count": 3,
                    "nodata": 0,
                    "crs": {"init": 'epsg:3857'},
                    "dtype": "uint8",
                    "compress": "deflate",
                    "height": big_image.shape[0],
                    "width": big_image.shape[1],
                    "transform": Affine(0.149, 0, self.tile_extents[0],
                                        0, -0.149, self.tile_extents[1])
                }
            )
            # self._write_tile_imagery(output_dir, big_image=big_image, index=f"{tile_index}", meta_data=meta_data)
            self._write_tile_imagery(output_dir,
                                     big_image=big_image,
                                     index=f"{tile_index}_{tile_iter}",
                                     meta_data=meta_data)
            del big_image

        del future

        # for y_idx in range(self.tile_count_y):
        #     for x_idx in range(self.tile_count_x):
        #         if x_idx == 0:
        #             tile = future[tile_count].result()
        #             tile_count += 1
        #         else:
        #             tile = np.append(tile, future[tile_count].result(), axis=1)
        #             tile_count += 1
        #     if y_idx == 0:
        #         big_image = tile
        #     else:
        #         big_image = np.append(big_image, tile, axis=0)
        #         del tile
        #
        # meta_data = dict()
        # meta_data.update(
        #     {
        #         "driver": "GTiff",
        #         "bigtiff": "YES",
        #         "count": 3,
        #         "nodata": 0,
        #         "crs": {"init": 'epsg:3857'},
        #         "dtype": "uint8",
        #         "compress": "deflate",
        #         "height": big_image.shape[0],
        #         "width": big_image.shape[1],
        #         "transform": Affine(0.149, 0, self.tile_extents[0],
        #                             0, -0.149, self.tile_extents[1])
        #     }
        # )
        # self._write_tile_imagery(output_dir, big_image=big_image, index=f"{tile_index}", meta_data=meta_data)
        # self._write_tile_imagery(output_dir, big_image=big_image, index=f"{tile_index}_{tile_iter}")
        # del big_image

    def _write_tile_imagery(self, output_dir, big_image, index, meta_data):

        self.file_path.append(os.path.join(output_dir, f"scene_{index}.tif"))
        with rasterio.open(
                os.path.join(output_dir, f"scene_{index}.tif"), "w", **meta_data
        ) as tiff_file:
            tiff_file.write(big_image[..., 0], 1)
            tiff_file.write(big_image[..., 1], 2)
            tiff_file.write(big_image[..., 2], 3)

    def upload_to_s3(self, config_path, bucket_name, output_dir):
        with open(config_path, "rb") as f:
            config = json.load(f)
        ACCESS_KEY = config["AWS_ACCESS_KEY_ID"]
        SECRET_KEY = config["AWS_SECRET_ACCESS_KEY"]
        s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        for file_path in self.file_path:
            file_name = file_path.split('/')[-1]
            output_file = os.path.join(output_dir, file_name)
            s3_client.upload_file(file_path,
                                  bucket_name,
                                  output_file,
                                  Callback=ProgressPercentage(file_path))

            print(f"{file_name} Upload Successful")
            os.remove(file_path)


if __name__ == '__main__':
    u_name = "phstangl@blackshark.ai"
    p_word = "93VYy3FKXxyaLMw!"
    url = "https://api.gic.org/auth/Login/"
    output_path = "/opt/project/data/vector/raw"
    vexcel_driver = VexcelImages(login_url=url,
                                 username=u_name,
                                 password=p_word)

    with open(
            "/opt/project/src/bsk/building_occupancy_roof_type_detection/configs/filtered_tiles.geojson"
    ) as filtered_polygon:
        filtered_dataframe = json.load(filtered_polygon)
    filtered_dataframe = gpd.GeoDataFrame.from_features(filtered_dataframe["features"])
    geoms = filtered_dataframe[filtered_dataframe["tile_index"] == "Tile-287_661"]["geometry"].iloc[0]
    polygon_list = vexcel_driver.get_tiled_bounding_box_wkt(bbox=geoms.bounds,
                                                            from_crs=4326,
                                                            to_crs=3857,
                                                            tile_size=200)

    vexcel_driver.get_ortho_image_tiles(output_dir=output_path,
                                        polygons=polygon_list,
                                        img_size=1340,
                                        tile_index="Tile-287_661",
                                        layer_type="bluesky-ultra",
                                        zoom=20
                                        )

    vexcel_driver.upload_to_s3(
        config_path="/opt/project/src/bsk/building_occupancy_roof_type_detection/configs/config.ini",
        bucket_name="mlteam-prod-s3-source",
        output_dir="occupancy_roof_type/occupancy_type"
    )


