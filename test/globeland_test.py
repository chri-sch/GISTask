from helperFunctions.gen_functions import getargs, get_tiles
import rasterio
import numpy as np


def globeland_processing(args):
    with rasterio.open(args.input_file) as src:
        profile = src.profile.copy()
        print("read data")
        data = src.read()
        print("convert band 1")
        # data[0, :, :] = np.where(data[0, :, :] == 255, 0, data[0, :, :])
        print("convert band 2")
        data[1, :, :] = np.where(data[1, :, :] == 255, 0, data[1, :, :])
        print("convert band 3")
        data[2, :, :] = np.where(data[2, :, :] == 255, 0, data[2, :, :])

    print("write data")
    with rasterio.open("out.tif", 'w', **profile) as outds:
        outds.write(data)


if __name__ == "__main__":
    globeland_processing(args=getargs())

