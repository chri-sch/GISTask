from shapely.geometry import box, Polygon

from helperFunctions.gen_functions import getargs, create_path, resample_raster, reproject_raster, \
    mask_raster_with_geometry
from os import listdir
from os.path import isfile, join
import os
from collections import defaultdict
from fiona.crs import from_epsg
import geopandas as gpd
import rasterio
import rasterio.mask
from rasterio.warp import calculate_default_transform, reproject, Resampling


def data_cropping(args):
    red_green_blue = {'LE07': ['B1.TIF', 'B2.TIF', 'B3.TIF'], 'LC08': ['B2.TIF', 'B3.TIF', 'B4.TIF']}
    geo_files = [f for f in listdir(args.output_path) if isfile(join(args.output_path, f))]
    dst_crs = 'EPSG:3857'

    bbox = {'north': 47.109626, 'south': 47.003436, 'east': 15.506172, 'west': 15.370560}

    # create geopandas bounding box
    lat_point_list = [bbox['north'], bbox['south'], bbox['south'], bbox['north']]
    lon_point_list = [bbox['west'], bbox['west'], bbox['east'], bbox['east']]
    bbox = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'},
                            geometry=[Polygon(zip(lon_point_list, lat_point_list))])

    print("reproject raster to epsg:3857 and clip to bbox extend of aoi for files:")
    create_path(os.path.join(args.output_path, "proj"))
    composite_dict = defaultdict(list)
    for file in geo_files:
        if file.split("_")[-1] in red_green_blue.get(file.split("_")[0], []):
            in_file = os.path.join(args.output_path, file)
            out_file_mask = os.path.join(args.output_path, 'mask', file.replace(".TIF", "_rasterio_mask.TIF"))

            print(f"   processing of {out_file_mask}")

            # open base file
            with rasterio.open(in_file) as src:
                # crop image
                bbox = bbox.to_crs(src.crs)

                out_image, out_transform = rasterio.mask.mask(src, bbox.geometry, crop=True)
                out_meta = src.meta
                out_meta.update({"driver": "GTiff",
                                 "height": out_image.shape[1],
                                 "width": out_image.shape[2],
                                 "transform": out_transform})

                # create_path(os.path.join(args.output_path, 'crop'))
                # with rasterio.open(out_file_crop, "w", **out_meta) as dest:
                #     dest.write(out_image)

                # reproject image
                proj_image, proj_transformation, proj_profile = reproject_raster(array=out_image[0], src_crs=src.crs,
                                                                                 dst_crs=dst_crs,
                                                                                 transform=out_transform,
                                                                                 resolution=(5, 5))

                # create building mask
                buildings = gpd.read_file("{}/buildings.gpkg".format(args.output_path), layer='buildings')
                create_path(os.path.join(args.output_path, 'mask'))
                mask_array, mask_meta = mask_raster_with_geometry(raster=proj_image.squeeze(0),
                                                                  transform=proj_transformation,
                                                                  shapes=buildings.geometry)
                with rasterio.open(out_file_mask, "w", **mask_meta) as mask:
                    mask.write(mask_array)


if __name__ == "__main__":
    data_cropping(args=getargs())
