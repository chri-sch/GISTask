import rasterio.warp
from rasterio.enums import Resampling
import rasterio.shutil
import scipy.ndimage

from helperFunctions.gen_functions import resample_raster

localname = 'LC08_L1TP_042034_20170616_20170629_01_T1_NDVI_OVIEW.tif'
vrtname = 'LC08_L1TP_042034_20170616_20170629_01_T1_NDVI_OVIEW_WGS84.vrt'

upscale_factor = 2

with rasterio.open(localname) as src:
    with rasterio.vrt.WarpedVRT(src, crs='epsg:4326', resampling=rasterio.enums.Resampling.bilinear) as vrt:
        rasterio.shutil.copy(vrt, vrtname, driver='VRT')

# Open the local warped file and plot
# NOTE our coordinates have changed to lat, lon. we should probably crop the edge artifacts do to reprojection too!
# with rasterio.open(vrtname) as src:
#     rasterio.plot.show(src, title='NDVI', cmap='RdYlGn', vmin=-1, vmax=1)

with rasterio.open(localname) as dataset:
    profile = dataset.profile.copy()

    # resample data to target shape
    data = dataset.read(
        out_shape=(
            dataset.count,
            int(dataset.height * upscale_factor),
            int(dataset.width * upscale_factor)
        ),
        resampling=Resampling.bilinear
    )

    test = dataset.read(
        out_shape=(
            dataset.count,
            int(dataset.height),
            int(dataset.width)
        ),
        resampling=Resampling.bilinear
    )

    # interpolation scipy with numpy input order 0 = nearest, 1 = bilinear, 3 = cubic
    test_res = scipy.ndimage.zoom(test[0], 2, order=1)

    # create a memory file object for in memory processing
    vergl, transformation_res = resample_raster(array=test[0], scaling_factor=2, resampling_method=Resampling.bilinear,
                                                transform=dataset.transform)

    # scale image transform
    transform = dataset.transform * dataset.transform.scale(
        (dataset.width / data.shape[-1]),
        (dataset.height / data.shape[-2])
    )

    profile.update({
        'dtype': 'float32',
        'height': data.shape[1],
        'width': data.shape[2],
        'transform': transformation_res})

    with rasterio.open('resampled.tif', 'w', **profile) as dst:
        dst.write_band(1, data[0])

    with rasterio.open('resampled2.tif', 'w', **profile) as dst:
        dst.write_band(1, test_res)

    with rasterio.open('resampled3.tif', 'w', **profile) as dst:
        dst.write_band(1, data[0])
