import rioxarray  # for the extension to load
import xarray
import rasterio
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon

from helperFunctions.gen_functions import getargs
import shapely

shapely.speedups.disable()

localname = 'D:\\PycharmProjects\\GISTask\\output\\LC08_L1TP_190027_20130618_20170503_01_T1_B1.TIF'
args = getargs()

bbox = {'north': 47.109626, 'south': 47.003436, 'east': 15.506172, 'west': 15.370560}

# create geopandas bounding box
lat_point_list = [bbox['north'], bbox['south'], bbox['south'], bbox['north']]
lon_point_list = [bbox['west'], bbox['west'], bbox['east'], bbox['east']]
bbox = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'},
                        geometry=[Polygon(zip(lon_point_list, lat_point_list))])
bbox = bbox.to_crs("EPSG:32633")

buildings = gpd.read_file("{}/buildings.gpkg".format(args.output_path), layer='buildings')

xds = xarray.open_dataset(localname)
xds = xds.rio.clip_box(
    minx=bbox.bounds.minx,
    miny=bbox.bounds.miny,
    maxx=bbox.bounds.maxx,
    maxy=bbox.bounds.maxy,
)
xds = xds.rio.reproject("EPSG:3857", resolution=(5, 5))


clipped = xds.rio.clip(buildings.geometry, buildings.crs, drop=False)
data = clipped.band_data.data

clipped.band_data.rio.to_raster("planet_scope_green.tif")
plt.imshow(data[0], cmap='RdYlGn')
plt.show()
