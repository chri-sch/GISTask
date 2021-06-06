import rasterio
import numpy as np
from rasterio.plot import show

url = 'https://gis.stmk.gv.at/arcgis/services/OGD/ALSGelaendeinformation_1m_UTM33N/MapServer/WmsServer?service=WMS&version=1.1.1&request=GetMap&layers=Gelaendehoehe_Gesamtmodell&styles=&width=1682&height=849&srs=EPSG:32633&bbox=515640.5190082641,5202075.827014463,551284.7214876037,5220046.445764463&format=image/png&transparent=FALSE&bgcolor=0xFFFFFF&exceptions=application/vnd.ogc.se_xml'

# url ='https://services.terrascope.be/wms/v2?service=WMS&version=1.3.0&request=GetMap&layers=CGS_S2_RADIOMETRY&format=image/png&time=2020-06-01&width=1920&height=592&bbox=556945.9710290054,6657998.9149440415,575290.8578174476,6663655.255037144&styles=&srs=EPSG:3857'

raster = rasterio.open("C:\\Users\\chri\\Documents\\clip.tif")

# print(raster.meta)
print(raster.transform[0])
print(raster.transform[1])
print(raster.transform[2])
print(raster.transform[3])
print(raster.transform[4])
print(raster.transform[5])
rasterio.Affine(raster.transform[0], raster.transform[1], raster.transform[2], raster.transform[3], raster.transform[4],
                raster.transform[5])
show(raster)

"""
516498.8203000000212342,
5165414.9053999995812774 : 
593041.2793000000528991,
5222964.1984000001102686
"""
