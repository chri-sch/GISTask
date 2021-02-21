from run.download_buildings import download_buildings
from run.download_data import download_data
from helperFunctions.gen_functions import getargs
from run.prepare_data import prepare_data

if __name__ == "__main__":

    # get arguments from argument parser
    arguments = getargs()

    # downloading remote sensing data
    download_data(arguments)

    # downloading osm buildings and create aoi layer
    download_buildings(arguments)

    # prepare data and store masked images to disk
    prepare_data(arguments)
