from argparse import ArgumentParser
import os
import sys
import tarfile
import rasterio
from rasterio.warp import calculate_default_transform, Resampling, reproject


def getargs(args_array=sys.argv[1:]):
    """ Argument parser
    :param args_array: Returns array with defined arguments
    :return:
    """
    default_path = os.path.dirname(__file__).split("helperFunctions")[0]

    parser = ArgumentParser(description='TODO: Description of this module')

    parser.add_argument("--input_path",
                        # action="store_true",
                        dest="input_path",
                        default=os.path.join(default_path, 'input'),
                        help="set input path")

    parser.add_argument("--max_cloud_cover",
                        # action="store_true",
                        dest="max_cloud_cover",
                        default=5,
                        help="set maximum cloud cover")

    parser.add_argument("--user",
                        # action="store_true",
                        dest="user",
                        default="chri",
                        help="earth explorer user name")

    parser.add_argument("--dataset",
                        # action="store_true",
                        dest="dataset",
                        default="LANDSAT_8_C1",
                        help="set dataset type for download (e.q. LANDSAT_TM_C1, LANDSAT_ETM_C1, LANDSAT_8_C1, and SENTINEL_2A)")

    parser.add_argument("--pwd",
                        # action="store_true",
                        dest="pwd",
                        default="B5tE86F9QVBiN8V",
                        help="earth explorer password")

    parser.add_argument("--relative_path",
                        # action="store_true",
                        dest="relative_path",
                        default=os.path.join(default_path, 'input'),
                        help="get relative_path")

    parser.add_argument("--output_path",
                        # action="store_true",
                        dest="output_path",
                        default=os.path.join(default_path, 'output'),
                        help="set output path")

    parser.add_argument("--output_file",
                        # action="store_true",
                        dest="output_file",
                        default=os.path.join(default_path, 'output'),
                        help="set output file")

    parser.add_argument("--start_date",
                        # action="store_true",
                        dest="start_date",
                        default='2002-10-01',
                        help="start date of search period")

    parser.add_argument("--end_date",
                        # action="store_true",
                        dest="end_date",
                        default='2014-10-30',
                        help="end date of search period")

    my_args = parser.parse_args(args_array)

    return my_args


def open_tarfile_function(path, filename):
    """Extracts zipped files

    :param path: file path
    :param filename: file name
    :return:
    """
    open_tarfile = tarfile.open(os.path.join(path, filename))
    open_tarfile.extractall(path=path)
    open_tarfile.close()


def create_path(path):
    """Creates file path if it not exists

    :param path: file path
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def resample_raster(array, scaling_factor, resampling_method, transform):
    """Wrapper for rasterio data set read method to allow for in-memory processing on numpy arrays.

    :param array: raster to be masked with dim: [height, width]
    :param scaling_factor: up or downscaling factor of array
    :param transform: rasterio transformation parameter
    :param resampling_method: rastario resampling method

    Returns:
        resampled numpy.ndarray with dim: [1, height, width]
        updated transformation parameters

    """
    # create a memory file object for in memory processing
    with rasterio.io.MemoryFile() as memory_file:
        with memory_file.open(
                driver='GTiff',
                height=array.shape[-2],
                width=array.shape[-1],
                count=1,
                dtype=array.dtype,
                transform=transform,
        ) as memory_dataset:
            memory_dataset.write(array, 1)
        with memory_file.open() as memory_dataset:
            # test = memory_dataset.read(1)
            memory_interpol = memory_dataset.read(
                out_shape=(
                    memory_dataset.count,
                    int(memory_dataset.height * scaling_factor),
                    int(memory_dataset.width * scaling_factor)
                ),
                resampling=resampling_method
            )

        # scale image transform
        transform = transform * transform.scale(
            (array.shape[-1] / memory_interpol.shape[-1]),
            (array.shape[-2] / memory_interpol.shape[-2])
        )

        return memory_interpol, transform


def reproject_raster(array, src_crs, dst_crs, transform, resolution=None, resampling_method=Resampling.bilinear):
    """Wrapper for rasterio data set read method to allow for in-memory reprojection on numpy arrays.

    :param array: raster to be reprojected with dim: [height, width]
    :param  src_crs: CRS or dict
        Source coordinate reference system, in rasterio dict format.
        Example: CRS({'init': 'EPSG:4326'})
    :param dst_crs: CRS or dict
        Target coordinate reference system.
    :param transform: rasterio transformation parameter
    :param resolution: tuple (x resolution, y resolution) or float, optional
        Target resolution, in units of target coordinate reference
        system. If None, target resolution is determined by rasterio 'calculate_default_transform' method
    :param resampling_method: rastario resampling method

    Returns:
        reprojected numpy.ndarray with dim: [1, height, width],
        updated transformation parameters,
        new profile meta data

    """

    # create a memory file object for in memory processing based on numpy array
    with rasterio.io.MemoryFile() as memory_file:
        with memory_file.open(
                driver='GTiff',
                height=array.shape[-2],
                width=array.shape[-1],
                count=1,
                dtype=array.dtype,
                transform=transform,
        ) as memory_dataset:
            memory_dataset.write(array, 1)
        with memory_file.open() as memory_dataset:
            # calculate transform parameter for reprojecting image
            transform, width, height = calculate_default_transform(src_crs, dst_crs,
                                                                   memory_dataset.width,
                                                                   memory_dataset.height,
                                                                   *memory_dataset.bounds,
                                                                   resolution=resolution)
            meta_data = memory_dataset.meta.copy()
            meta_data.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            # # with rasterio.io.MemoryFile().open as memory_file:
            # with rasterio.open('reprojected_888.tif', 'w+', **meta_data) as dst:
            #     print()
            #     reproject(
            #         source=memory_dataset.read(),
            #         destination=rasterio.band(dst, 1),
            #         src_transform=memory_dataset.transform,
            #         src_crs=src_crs,
            #         dst_transform=transform,
            #         dst_crs=dst_crs,
            #         resampling=resampling_method)
            #     print()

            # in memory
            with rasterio.io.MemoryFile() as repr_des:
                with repr_des.open(**meta_data) as repr_dataset:
                    reproject(
                        source=memory_dataset.read(),
                        destination=rasterio.band(repr_dataset, 1),
                        src_transform=memory_dataset.transform,
                        src_crs=src_crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=resampling_method)

                    return repr_dataset.read(), repr_dataset.transform, repr_dataset.profile


def mask_raster_with_geometry(raster, transform, shapes, **kwargs):
    """Wrapper for rasterio.mask.mask to allow for in-memory processing.

    Docs: https://rasterio.readthedocs.io/en/latest/api/rasterio.mask.html

    Args:
        raster (numpy.ndarray): raster to be masked with dim: [H, W]
        transform (affine.Affine): the transform of the raster
        shapes, **kwargs: passed to rasterio.mask.mask

    Returns:
        masked: numpy.ndarray or numpy.ma.MaskedArray with dim: [H, W]
    """
    with rasterio.io.MemoryFile() as memfile:
        with memfile.open(
            driver='GTiff',
            height=raster.shape[0],
            width=raster.shape[1],
            count=1,
            dtype=raster.dtype,
            transform=transform,
        ) as dataset:
            dataset.write(raster, 1)
        with memfile.open() as dataset:
            output, _ = rasterio.mask.mask(dataset, shapes, **kwargs)
    return output, dataset.meta
