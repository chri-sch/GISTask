from owslib.wms import WebMapService
from rasterio import MemoryFile
from rasterio.plot import show
import sys


def download_wms():
    url = 'https://gis.stmk.gv.at/arcgis/services/OGD/ALSGelaendeinformation_1m_UTM33N/MapServer/WMSServer'
    wms = WebMapService(url)
    """
    https://gis.stmk.gv.at/arcgis/services/OGD/ALSGelaendeinformation_1m_UTM33N/MapServer/WMSServer?service
    =WMS&request=GetMap&version=1.3.0&BGCOLOR=0xFFFFFF&crs=
    EPSG:32633&bbox=
    515640.5190082641,
    5202075.827014463,
    551284.7214876037,
    5220046.445764463
    &layers=Gelaendehoehe_Gesamtmodell&width=1682&height=849&format=image/bmp
    """

    print(list(wms.contents))

    x_min = 515640.5190082641
    y_min = 5202075.827014463
    x_max = 551284.7214876037
    y_max = 5220046.445764463

    layer = 'Gelaendehoehe_Gesamtmodell'

    # sys.exit(0)
    img = wms.getmap(
        layers=[layer],
        srs='EPSG:32633',
        bbox=(x_min, y_min, x_max, y_max),
        size=(1682, 849),
        format='image/png'
    )
    out = open('jpl_mosaic_visb.jpg', 'wb')
    out.write(img.read())
    out.close()

    with MemoryFile(img) as memfile:
        with memfile.open() as dataset:
            show(dataset)
            print(dataset.profile)


def download_wms_example():
    url = 'https://services.terrascope.be/wms/v2?'
    # url = 'https://gis.stmk.gv.at/arcgis/services/OGD/ALSGelaendeinformation_1m_UTM33N/MapServer/WMSServer'
    wms = WebMapService(url)

    print(list(wms.contents))

    x_min = 556945.9710290054
    y_min = 6657998.9149440415
    x_max = 575290.8578174476
    y_max = 6663655.255037144

    layer = 'CGS_S2_RADIOMETRY'

    # sys.exit(0)
    img = wms.getmap(
        layers=[layer],
        srs='EPSG:3857',
        bbox=(x_min, y_min, x_max, y_max),
        size=(1920, 592),
        format='image/png',
        time='2020-06-01'
    )

    with MemoryFile(img) as memfile:
        with memfile.open() as dataset:
            show(dataset)
            print(dataset.profile)


if __name__ == "__main__":
    # download_wms_example()
    download_wms()
    print()
