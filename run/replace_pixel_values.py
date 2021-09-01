import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import glob
import os

from helperFunctions.gen_functions import getargs


def replace_values(args):
    search_criteria = "*.tif"
    q = os.path.join(args.input_path, search_criteria)

    files = glob.glob(q)

    for file in files:
        print(file)
        profile = None
        data = None
        with rasterio.open(file) as src:
            data = src.read()
            profile = src.profile.copy()

        with rasterio.open(file, 'w', **profile) as dest:
            print()
            dest.write(data)


if __name__ == "__main__":
    replace_values(getargs())