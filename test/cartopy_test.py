import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.io.ogc_clients import WMTSRasterSource
from owslib.wmts import WebMapTileService

import requests
from requests.auth import HTTPBasicAuth

def main():
    url = 'https://securewatch.maxar.com/earthservice/wmtsaccess?connectId=1b947d5d-2e2b-404a-ae60-b10802511e80&LAYER=DigitalGlobe:ImageryTileService&featureProfile=Vivid_2020'
    wmts = WebMapTileService(url=url, username='shs@blackshark.ai', password='f+pd2fDKxEJ6J7bB')

    requests.get(url=url, auth=HTTPBasicAuth('shs@blackshark.ai', 'f+pd2fDKxEJ6J7bB'))

    wmts.gettile(layer="DigitalGlobe:ImageryTileService",
                 tilematrixset="EPSG:3857",
                 tilematrix="EPSG:3857:12",
                 row=1550, column=3372)
    print()


    # url = 'https://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'
    # url = 'https://gis.stmk.gv.at/arcgis/rest/services/OGD/FranziszeischerKatasterSteiermark/MapServer/WMTS/'
    url = 'https://basemap.at/wmts/1.0.0/WMTSCapabilities.xml'
    # url = 'http://maps.wien.gv.at/wmts/1.0.0/WMTSCapabilities.xml'
    # layer = 'VIIRS_CityLights_2012'
    # layer = 'OGD_FranziszeischerKatasterSteiermark'
    layer = 'bmaporthofoto30cm'
    # layer = 'lb2018'

    # wms = WMSRasterSource(url, layer)

    ax = plt.axes(projection=ccrs.UTM(zone="33N"))
    # ax = plt.axes(projection=ccrs.PlateCarree())
    grid_lines = ax.gridlines(draw_labels=True)
    grid_lines.xformatter = LONGITUDE_FORMATTER
    grid_lines.yformatter = LATITUDE_FORMATTER
    ax.add_wmts(url, layer)

    ax.set_extent((560701.6, 562593.4, 5275300.3, 5276521.4), crs=ccrs.UTM(zone="33N"))
    # ax.set_extent((1718062.37, 1719164.72, 5953859.98, 5954406.52), crs=ccrs.GOOGLE_MERCATOR)

    plt.title('Suomi NPP Earth at night April/October 2012')
    plt.show()


if __name__ == '__main__':
    main()
