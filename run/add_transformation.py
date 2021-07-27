from helperFunctions.gen_functions import getargs, add_bbox_transformation
import geopandas as gpd
from pathlib import Path
import shapely
import rasterio
import pandas as pd
import os
import numpy as np
from rasterio.warp import calculate_default_transform

shapely.speedups.disable()


def add_transformation(args):
    quad_keys = pd.read_csv(args.input_file, delimiter=';', dtype=str)
    file_name = Path(args.input_file).name
    file_path = args.input_file.split(file_name)[0]

    # bbox = gpd.read_file(args.input_geo_file)

    def add_projection(df, path):
        # file names
        merged_file = os.path.join(path, df['name'], "merged.png")
        processed_file = os.path.join(path, df['name'], "processed.png")

        merged_file_out = merged_file.replace(".png", "_proj.tif")
        processed_file_out = processed_file.replace(".png", "_proj.tif")

        # read tile grid from folder

        if not os.path.isfile(merged_file_out) and not os.path.isfile(processed_file_out):
            tile_grid_file = os.path.join(path, df['name'], f"{df['name']}.gpkg")
            tile_grid = gpd.read_file(tile_grid_file, layer=df['name'])

            # find upper left and lower right tile from tile grid
            upper_left = tile_grid[tile_grid.quadkey == df.upper_left]
            lower_right = tile_grid[tile_grid.quadkey == df.lower_right]

            if "USA_Miami" in processed_file_out:
                print()

            bbox = (
                upper_left.bounds.minx.values[0], lower_right.bounds.miny.values[0], lower_right.bounds.maxx.values[0],
                upper_left.bounds.maxy.values[0])

            print(f"add projection to {merged_file}")
            if not os.path.isfile(merged_file_out):
                add_bbox_transformation(in_file=merged_file, out_file=merged_file_out, bbox=bbox)

            print(f"add projection to {processed_file}")
            if not os.path.isfile(processed_file_out):
                add_bbox_transformation(in_file=merged_file, out_file=processed_file_out, bbox=bbox)

    quad_keys.apply(add_projection, path=file_path, axis=1)


if __name__ == "__main__":
    add_transformation(args=getargs())
