import glob
import rasterio
import os

files_to_mosaic = glob.glob(r'C:\temp\*.tif')

for file in files_to_mosaic:

    with rasterio.open(file) as src:
        meta = src.meta.copy()
        meta.update({"driver": "JP2OpenJPEG"})
        meta.update({'count': 3})

        new_name = file.split('\\')[-1].split('.tif')[0] + ".jp2"
        new_path = os.path.join(r"C:\temp\jpg", new_name)
        print(file, "-->", new_path)
        with rasterio.open(new_path, 'w', **meta) as dst:
            dst.write(src.read()[0:3, :, :])

