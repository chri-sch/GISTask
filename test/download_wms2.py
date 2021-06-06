from io import BytesIO

from owslib.wms import WebMapService
import rasterio
from rasterio import MemoryFile
from rasterio.plot import show

url = 'http://geodata.nationaalgeoregister.nl/ahn3/wms?service=wms&version=1.3.0'
wms = WebMapService(url)

x1new= 100000
x2new = 100500
y1new = 450000
y2new = 450500

layer= 'ahn3_05m_dtm'


img = wms.getmap(layers = [layer], srs = 'EPSG:28992', bbox = [x1new,y1new,x2new,y2new] , size = (1920, 592), format= 'image/GeoTIFF')

with rasterio.open(BytesIO(img.read())) as r:
    thing = r.read()
    show(thing)