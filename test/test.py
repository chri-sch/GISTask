import rasterio
import numpy as np

TMS_dataset = rasterio.open(
    'https://gis.stmk.gv.at/arcgis/services/OGD/ALSGelaendeinformation_1m_UTM33N/MapServer/WmsServer?service=WMS&version=1.1.1&request=GetMap&layers=Gelaendehoehe_Gesamtmodell&styles=&width=1682&height=849&srs=EPSG:32633&bbox=515640.5190082641,5202075.827014463,551284.7214876037,5220046.445764463&format=image/png&transparent=FALSE&bgcolor=0xFFFFFF&exceptions=application/vnd.ogc.se_xml')

with rasterio.open('resampled.tif', 'w', **profile) as dst:
    dst.write_band(1, data[0])

# Calculate the pixel positions of the desired bounding box at the highest zoom level
# as specified in the XML file.
bl = TMS_dataset.index(west, south, op=math.floor)
tr = TMS_dataset.index(east, north, op=math.ceil)
# image_size is a tuple (h, w, num_bands)
output_dataset = np.empty(shape=image_size, dtype=TMS_dataset.profile['dtype'])

# Read each band
TMS_dataset.read(1, out=output_dataset[:, :, 0], window=((tr[0], bl[0]), (bl[1], tr[1])))
TMS_dataset.read(2, out=output_dataset[:, :, 1], window=((tr[0], bl[0]), (bl[1], tr[1])))
TMS_dataset.read(3, out=output_dataset[:, :, 2], window=((tr[0], bl[0]), (bl[1], tr[1])))

# Create an output image dataset
output_image = rasterio.open('flange3.png', 'w', driver='png', width=image_size[1], height=image_size[0], count=3,
                             dtype=output_dataset.dtype)
# Write each band
output_image.write(output_dataset[:, :, 0], 1)
output_image.write(output_dataset[:, :, 1], 2)
output_image.write(output_dataset[:, :, 2], 3)

output_image.close()
