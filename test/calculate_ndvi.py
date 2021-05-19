import rasterio
import rasterio.plot
import pyproj
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Use the same example image:
date = '2017-06-16'
url = 'http://landsat-pds.s3.amazonaws.com/c1/L8/042/034/LC08_L1TP_042034_20170616_20170629_01_T1/'
redband = 'LC08_L1TP_042034_20170616_20170629_01_T1_B{}.TIF'.format(4)
nirband = 'LC08_L1TP_042034_20170616_20170629_01_T1_B{}.TIF'.format(5)

with rasterio.open(url + redband) as src:
    profile = src.profile
    oviews = src.overviews(1)  # list of overviews from biggest to smallest
    oview = oviews[1]  # Use second-highest resolution overview
    print('Decimation factor= {}'.format(oview))
    red = src.read(1, out_shape=(1, int(src.height // oview), int(src.width // oview)))

# plt.imshow(red)
# plt.colorbar()
# plt.title('{}\nRed {}'.format(redband, red.shape))
# plt.xlabel('Column #')
# plt.ylabel('Row #')

with rasterio.open(url + nirband) as src:
    oviews = src.overviews(1)  # list of overviews from biggest to smallest
    oview = oviews[1]  # Use second-highest resolution overview
    nir = src.read(1, out_shape=(1, int(src.height // oview), int(src.width // oview)))


# plt.imshow(nir)
# plt.colorbar()
# plt.title('{}\nNIR {}'.format(nirband, nir.shape))
# plt.xlabel('Column #')
# plt.ylabel('Row #')


def calc_ndvi(nir, red):
    '''Calculate NDVI from integer arrays'''
    nir = nir.astype('f4')
    red = red.astype('f4')
    ndvi = (nir - red) / (nir + red)
    return ndvi


ndvi = calc_ndvi(nir, red)
plt.imshow(ndvi, cmap='RdYlGn')
plt.colorbar()
plt.title('NDVI {}'.format(date))
plt.xlabel('Column #')
plt.ylabel('Row #')
# plt.show()

localname = 'LC08_L1TP_042034_20170616_20170629_01_T1_NDVI_OVIEW.tif'

with rasterio.open(url + nirband) as src:
    profile = src.profile.copy()

    aff = src.transform
    newaff = rasterio.Affine(aff.a * oview, aff.b, aff.c,
                             aff.d, aff.e * oview, aff.f)
    profile.update({
        'dtype': 'float32',
        'height': ndvi.shape[0],
        'width': ndvi.shape[1],
        'transform': newaff})

    with rasterio.open(localname, 'w', **profile) as dst:
        dst.write_band(1, ndvi)

# Reopen the file and plot
# with rasterio.open(localname) as src:
#     print(src.profile)
#     ndvi = src.read(1) # read the entire array

# plt.imshow(ndvi, cmap='RdYlGn')
# plt.colorbar()
# plt.title('NDVI {}'.format(date))
# plt.xlabel('Column #')
# plt.ylabel('Row #')

# spatial indexing
with rasterio.open(localname) as src:
    # Use pyproj to convert point coordinates
    utm = pyproj.Proj(src.crs)  # Pass CRS of image from rasterio
    lonlat = pyproj.Proj(init='epsg:4326')

    lon, lat = (-119.770163586, 36.741997032)
    east, north = pyproj.transform(lonlat, utm, lon, lat)

    print('Fresno NDVI\n-------')
    print(f'lon,lat=\t\t({lon:.2f},{lat:.2f})')
    print(f'easting,northing=\t({east:g},{north:g})')

    # What is the corresponding row and column in our image?
    row, col = src.index(east, north)  # spatial --> image coordinates
    print(f'row,col=\t\t({row},{col})')

    # What is the NDVI?
    value = ndvi[row, col]
    print(f'ndvi=\t\t\t{value:.2f}')

    # Or if you see an interesting feature and want to know the spatial coordinates:
    row, col = 200, 450
    east, north = src.xy(row, col)  # image --> spatial coordinates
    lon, lat = pyproj.transform(utm, lonlat, east, north)
    value = ndvi[row, col]
    print(f'''
Interesting Feature
-------
row,col=          ({row},{col})
easting,northing= ({east:g},{north:g})
lon,lat=          ({lon:.2f},{lat:.2f})
ndvi=              {value:.2f}
''')
