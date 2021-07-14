from owslib.wmts import WebMapTileService
from pygeotile.point import Point
from pygeotile.tile import Tile
import numpy as np
import math
from helperFunctions.gen_functions import _tile_span

# Standard pixel size of 0.28 mm as defined by WMTS.
METERS_PER_PIXEL = 0.28e-3
_WGS84_METERS_PER_UNIT = 2 * math.pi * 6378137 / 360

METERS_PER_UNIT = {
    'urn:ogc:def:crs:EPSG::27700': 1,
    'urn:ogc:def:crs:EPSG::900913': 1,
    'urn:ogc:def:crs:OGC:1.3:CRS84': _WGS84_METERS_PER_UNIT,
    'urn:ogc:def:crs:EPSG::3031': 1,
    'urn:ogc:def:crs:EPSG::3413': 1,
    'urn:ogc:def:crs:EPSG::3857': 1,
    'urn:ogc:def:crs:EPSG:6.18.3:3857': 1
}

meter_x, meter_y, zoom = 1548680, 6035771, '11'  # meters in Spherical Mercator EPSG:900913

# point = Point.from_meters(meter_x=meter_x, meter_y=meter_y)
# print('Pixels: ', point.pixels(zoom=zoom))
# print('Lat/Lon: ', point.latitude_longitude)

# tile = Tile.for_meters(meter_x=meter_x, meter_y=meter_y, zoom=zoom)
# tile2 = Tile.for_latitude_longitude(latitude=48.2747283, longitude=16.1704925, zoom=zoom)
# point = Point.from_latitude_longitude(latitude=48.2747283, longitude=16.1704925)
# tile = Tile.for_point(point, zoom=zoom)

wms = WebMapTileService('https://gis.stmk.gv.at/arcgis/rest/services/OGD/FranziszeischerKatasterSteiermark/MapServer/WMTS/')
pixel_span = wms.tilematrixsets['default028mm'].tilematrix[zoom].scaledenominator * 0.00028

span_x = wms.tilematrixsets['default028mm'].tilematrix[zoom].tilewidth * pixel_span
span_y = wms.tilematrixsets['default028mm'].tilematrix[zoom].tileheight * pixel_span

tl = wms.tilematrixsets['default028mm'].tilematrix[zoom].topleftcorner
minx, maxy = wms.tilematrixsets['default028mm'].tilematrix[zoom].topleftcorner

maxx = minx + span_x * wms.tilematrixsets['default028mm'].tilematrix[zoom].matrixwidth
miny = maxy - span_y * wms.tilematrixsets['default028mm'].tilematrix[zoom].matrixheight

xcoords = np.arange(minx, maxx, span_x)
ycoords = np.arange(miny, maxy, span_y)
ycoords = ycoords[::-1]

idx = np.where(meter_x >= xcoords)[0][-1]
idy = np.where(meter_y <= ycoords)[0][-1]
print(f"top left: {minx} {maxy}, lower right: {maxx} {miny}")
print(f"idy: {idy}, idx: {idx}")
# print(pixel_span, tile_span_x, tile_span_y)

tile_matrix = wms.tilematrixsets['default028mm'].tilematrix[zoom]
meters_per_unit = METERS_PER_UNIT[wms.tilematrixsets['default028mm'].crs]
# Determine which tiles are required to cover the requested extent.
tile_span_x, tile_span_y = _tile_span(tile_matrix, meters_per_unit)

layer = wms.contents['OGD_FranziszeischerKatasterSteiermark']
tile_matrix_set_links = getattr(layer, 'tilematrixsetlinks', None)
if tile_matrix_set_links is None:
    tile_matrix_limits = None
else:
    tile_matrix_set_link = tile_matrix_set_links['default028mm']
    tile_matrix_limits = tile_matrix_set_link.tilematrixlimits.get(
        tile_matrix.identifier)
print()
