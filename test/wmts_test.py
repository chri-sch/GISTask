from owslib.wmts import WebMapTileService

wmts = WebMapTileService('https://maps.wien.gv.at/basemap/1.0.0/WMTSCapabilities.xml')
img = wmts.gettile(layer='v0Lw1953KMdH',
                   tilematrixset='WGS84',
                   tilematrix='16',
                   row='20480',
                   column='32001',
                   format='image/tif')