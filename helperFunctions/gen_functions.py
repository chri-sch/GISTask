from argparse import ArgumentParser
import os
import sys
import tarfile


def getargs(args_array=sys.argv[1:]):
    default_path = os.path.dirname(__file__).split("helperFunctions")[0]

    parser = ArgumentParser(description='TODO: Description of this module')

    parser.add_argument("--input_path",
                        # action="store_true",
                        dest="input_path",
                        default=os.path.join(default_path, 'input'),
                        help="set input path")

    parser.add_argument("--input_file",
                        # action="store_true",
                        dest="input_file",
                        default=os.path.join(default_path, 'input'),
                        help="set input file")

    parser.add_argument("--user",
                        # action="store_true",
                        dest="user",
                        default="user",
                        help="earth explorer user name")

    parser.add_argument("--linkstats_file2",
                        # action="store_true",
                        dest="linkstats_file2",
                        default=os.path.join(default_path, 'input'),
                        help="set input linkstats file")

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

    parser.add_argument("--counts_file",
                        # action="store_true",
                        dest="counts_file",
                        default=os.path.join(default_path, 'input'),
                        help="set input counts file")

    parser.add_argument("--network_file",
                        # action="store_true",
                        dest="network_file",
                        default=os.path.join(default_path, 'input'),
                        help="set input network file")

    parser.add_argument("--table_name",
                        # action="store_true",
                        dest="table_name",
                        default=os.path.join(default_path, 'input'),
                        help="set input table name from PostgreSql database")

    parser.add_argument("--study_area",
                        # action="store_true",
                        dest="study_area",
                        default=os.path.join(default_path, 'input'),
                        help="set input study area file")

    parser.add_argument("--bool_test",
                        # action="store_true",
                        dest="b_test",
                        # default="",
                        type=bool,
                        help="set output path")

    parser.add_argument("--int_test",
                        # action="store_true",
                        dest="i_test",
                        default=0,
                        type=int,
                        help="set output path")

    parser.add_argument("--float_test",
                        # action="store_true",
                        dest="f_test",
                        default=0,
                        type=float,
                        help="set output path")

    myargs = parser.parse_args(args_array)

    return myargs


def open_tarfile_function(path, filename):
    open_tarfile=tarfile.open(os.path.join(path, filename))
    open_tarfile.extractall(path=path)
    open_tarfile.close()
