import osmnx as ox
import geopandas as gpd
import os
from helperFunctions.gen_functions import getargs, create_path
from shapely.geometry import Polygon


def download_buildings(args):
    """Downloads OSM buildings based on defined bounding box and filters buildings with height

    :param args: arguments from argument parser
    :return:
    """

    bbox = {'north': 47.109626, 'south': 47.003436, 'east': 15.506172, 'west': 15.370560}
    tags = {'building': True}

    create_path(args.output_path)
    buildings_file = os.path.join(args.output_path, "buildings.gpkg")

    print("create bounding box...")

    lat_point_list = [bbox['north'], bbox['south'], bbox['south'],  bbox['north']]
    lon_point_list = [bbox['west'], bbox['west'], bbox['east'],  bbox['east']]

    # create geopandas frame from bounding box
    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    crs = {'init': 'epsg:4326'}
    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom]).to_crs("EPSG:3857")
    print(polygon.geometry)

    # write bbox layer to building.gpkg
    polygon.to_file(buildings_file, layer='bbox', driver="GPKG")
    print("done...")
    print()

    # specify that we're retrieving building footprint geometries an filter buildings which contain height values
    print("download osm data and prepare data set")
    gdf = ox.geometries_from_bbox(north=bbox['north'], south=bbox['south'], east=bbox['east'], west=bbox['west'],
                                  tags=tags)
    gdf = ox.project_gdf(gdf)

    # remove buildings with no height from frame
    gdf = gdf[gdf.height.notna()]

    # Just keep height attribute and transform to epsg: 3857
    gdf.drop(gdf.columns.difference(['unique_id', 'geometry', 'height']), 1, inplace=True)
    gdf = gdf.to_crs("EPSG:3857")

    # write buildings layer to building.gpkg
    gdf.to_file(buildings_file, layer='buildings', driver="GPKG")
    print("done...")
    print()


if __name__ == "__main__":
    download_buildings(getargs())
