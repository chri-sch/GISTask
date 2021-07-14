import cartopy.crs as ccrs
import matplotlib.pyplot as plt


def main():
    url = 'https://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'
    # url = 'https://gis.stmk.gv.at/arcgis/rest/services/OGD/FranziszeischerKatasterSteiermark/MapServer/WMTS/'
    layer = 'VIIRS_CityLights_2012'
    # layer = 'OGD_FranziszeischerKatasterSteiermark'

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_wmts(url, layer)
    ax.set_extent((-5, 25, 35, 60))
    # ax.set_extent((13.7863, 47.2930, 14.03531, 47.51624))

    plt.title('Suomi NPP Earth at night April/October 2012')
    plt.show()


if __name__ == '__main__':
    main()
