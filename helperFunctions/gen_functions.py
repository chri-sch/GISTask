from argparse import ArgumentParser
import os
import sys
import tarfile


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
                        default="user",
                        help="earth explorer user name")

    parser.add_argument("--dataset",
                        # action="store_true",
                        dest="dataset",
                        default="LANDSAT_8_C1",
                        help="set dataset type for download (e.q. LANDSAT_TM_C1, LANDSAT_ETM_C1, LANDSAT_8_C1, and SENTINEL_2A)")

    parser.add_argument("--pwd",
                        # action="store_true",
                        dest="pwd",
                        default=os.path.join(default_path, 'input'),
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
                        default='2003-10-30',
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
