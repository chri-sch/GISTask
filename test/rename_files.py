import geopandas as gpd
import os
import shutil
import rasterio
from osgeo import gdal

df = gpd.read_file(r"C:\QGIS_Projects\data\Orlando_tile_index.geojson")
for nr, row in df.iterrows():
    path = r"C:\temp\ortho"
    path_new = r"C:\temp\ortho\new"
    path_store = r"C:\temp\ortho\new"

    filen_old = os.path.join(path, f"orlando_ortho-nir_{row.fid}.tif")
    filen_new = os.path.join(path_new, f"orlando_ortho-nir_bluesky-ultra{row.file_numbe}.tif")

    filen_store = os.path.join(path_store, f"orlando_dsm_{row.file_numbe}.tif")

    if os.path.isfile(filen_old):
        shutil.move(filen_old, filen_new)
        print(filen_old, " -> ", filen_new)

        # vrt_path = filen_new.replace(".tif", ".vrt")
        # vrt = gdal.BuildVRT(vrt_path, filen_new)
        # translate_option = gdal.TranslateOptions(gdal.ParseCommandLine(
        #     "-of GTiff -co BIGTIFF=YES -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 -co NUM_THREADS=ALL_CPUS"))
        # gdal_result = gdal.Translate(filen_store, vrt, format='GTiff', options=translate_option)
        # gdal_result.BuildOverviews("AVERAGE", [2, 4, 8, 16, 32, 64])
        # gdal_result = None
        # vrt = None

        # ds_Raster = gdal.Open(filen_new)
        # band = ds_Raster.GetRasterBand(1)
        # band.SetNoDataValue(-9999)
        # ds_Raster = None

        meta_data_dict = {"nodata": 9999}
        with rasterio.open(filen_new, 'r+') as src:
            # src.update_tags(**meta_data_dict)
            src.nodata = None
