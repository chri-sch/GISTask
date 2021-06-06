from owslib.wms import WebMapService
from rasterio import MemoryFile, Affine
from rasterio.plot import show
import rasterio
from rasterio.warp import calculate_default_transform
import sys


def download_wms():
    url = 'https://gis.stmk.gv.at/arcgis/services/OGD/ALSGelaendeinformation_1m_UTM33N/MapServer/WMSServer'
    # url = 'https://data.wien.gv.at/daten/geo?version=1.3.0'
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
    print()
    print(wms.getOperationByName('GetMap').methods)
    print(wms.getOperationByName('GetMap').formatOptions)
    print()

    # Wien
    x_min = 16.273974736842106
    y_min = 48.237936798891965
    x_max = 16.395343684210523
    y_max = 48.31535741163435
    size = (1427, 911)
    crs = 'EPSG:4326'
    layer = 'ogdwien:FLIESSGEWOGD'

    # Land Steiermark
    x_min = 520490.8610143307
    y_min = 5297719.1287194025
    x_max = 520934.7048942241
    y_max = 5298002.2543943655
    size = (1427, 911)
    crs = 'EPSG:32633'

    # x_min = 517813.4903421879
    # y_min = 5224486.282982498
    # x_max = 530691.5979046926
    # y_max = 5232701.160017107
    # size = (1427, 911)
    # crs = 'EPSG:32633'
    layer = 'Gelaendehoehe_Gesamtmodell'
    print(wms[layer].styles)

    # sys.exit(0)
    img = wms.getmap(
        layers=[layer],
        srs=crs,
        bbox=(x_min, y_min, x_max, y_max),
        size=size,
        format='image/tiff'
    )
    # out = open('jpl_mosaic_visb.jpg', 'wb')
    # out.write(img.read())
    # out.close()

    x_res = (x_max - x_min) / size[0]
    y_res = (y_max - y_min) / size[1]

    transform, width, height = calculate_default_transform(crs, crs,
                                                           size[0],
                                                           size[1],
                                                           *[x_min, y_min, x_max, y_max])

    with MemoryFile(img) as memfile:
        with memfile.open() as dataset:
            print(dataset.profile)
            meta_data = dataset.meta.copy()
            meta_data.update({
                'crs': crs,
                'transform': transform,
                'width': size[0],
                'height': size[1]
            })
            show(dataset)
            with rasterio.open("subset.tif", 'w', **meta_data) as outds:
                outds.write(dataset.read())
            print()


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
