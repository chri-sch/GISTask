import rasterio
from rasterio.warp import reproject, Resampling
import boto3
from rasterio.session import AWSSession
from helperFunctions.gen_functions import getargs


ortho_file = r's3://mlteam-prod-s3-source/occupancy_roof_type/occupancy_type/scene_215_63.tif'
dsm_file = r'C:\_data\vexcel\_resample\dsm_4326.tif'
out_file = r'C:\_data\vexcel\_resample\dsm_out1.tif'

args = getargs()

boto3_session = boto3.Session(
    aws_access_key_id=args.aws_access_key_id,
    aws_secret_access_key=args.aws_secret_access_key)

with rasterio.Env(AWSSession(boto3_session)) as env:
    print("read meta data from file stored on the S3")
    with rasterio.open(ortho_file, mode='r') as src:
        kwargs = src.meta.copy()

        # reproject and resample dsm grid to source grid
        print("reproject and resample dsm grid to source grid")
        with rasterio.open(dsm_file) as dsm:
            # update meta data
            kwargs.update({"count": dsm.count})
            kwargs.update({"dtype": dsm.meta['dtype']})

            with rasterio.open(out_file, 'w', **kwargs) as dst:
                for i in range(1, dsm.count + 1):
                    reproject(
                        source=rasterio.band(dsm, i),
                        destination=rasterio.band(dst, i),
                        src_transform=dsm.transform,
                        src_crs=dsm.crs,
                        dst_transform=src.transform,
                        dst_crs=src.crs,
                        resampling=Resampling.nearest)
print("done...")
