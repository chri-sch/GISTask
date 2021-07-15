from owslib.wmts import WebMapTileService
import requests
from pygeotile.tile import Tile
from pygeotile.point import Point

from helperFunctions.gen_functions import deg2num

url = 'https://gis.stmk.gv.at/arcgis/rest/services/OGD/FranziszeischerKatasterSteiermark/MapServer/WMTS/'
# http://maps.wien.gv.at/wmts/1.0.0/WMTSCapabilities.xml
wmts = WebMapTileService(url=url, version="1.0.0")
print(wmts.identification.type)

content = sorted(list(wmts.contents))[0]
tile_matrix = wmts.tilematrixsets['default028mm']
print(sorted(list(wmts.contents))[0])
print(wmts.contents[content].styles)

zoom = 19
x_tile, y_tile = deg2num(lat_deg=47.0042650, lon_deg=15.2839186, zoom=zoom)
tile = Tile.for_point(point=Point.from_latitude_longitude(latitude=47.0042650, longitude=15.2839186), zoom=zoom)
tile2 = Tile.for_point(point=Point.from_meters(meter_x=1701318.46, meter_y=5942654.21), zoom=zoom)


print()

# tile = wmts.gettile(layer='OGD_FranziszeischerKatasterSteiermark',
#                     tilematrixset='default028mm',
#                     tilematrix='0',
#                     style='default',
#                     row=1,
#                     column=1,
#                     format="image/png")

# r = requests.get('https://api.github.com/user')

'https://gis.stmk.gv.at/arcgis/rest/services/OGD/FranziszeischerKatasterSteiermark/MapServer/WMTS/tile/1.0.0/OGD_FranziszeischerKatasterSteiermark/{Style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.png'


url = f'https://gis.stmk.gv.at/arcgis/rest/services/OGD/FranziszeischerKatasterSteiermark/MapServer/WMTS/tile/1.0.0/OGD_FranziszeischerKatasterSteiermark/default/default028mm/{zoom}/{tile2.tms_y}/{tile2.tms_x}.png'
print(url)
