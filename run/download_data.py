import landsatxplore.api
from landsatxplore.earthexplorer import EarthExplorer
import os
from helperFunctions.gen_functions import open_tarfile_function, getargs, create_path


def download_data(args):
    """Downloads remote sensing data from EarthExplorer platform

    :param args: arguments from argument parser
    :return:
    """

    # set user and password of your account
    usr_pw = {'user': args.user, 'password': args.pwd}

    # Initialize a new API instance and get an access key
    api = landsatxplore.api.API(usr_pw['user'], usr_pw['password'])

    # Finding scenes for Graz (47.069888, 15.437851)
    scenes = api.search(
        dataset=args.dataset,
        latitude=17.5473,
        longitude=-92.5043,
        start_date=args.start_date,
        end_date=args.end_date,
        max_cloud_cover=args.max_cloud_cover)

    # start_date = '2019-10-01',
    # end_date = '2019-10-30')
    print('{} scenes found.'.format(len(scenes)))
    api.logout()

    # download data from earth explorer by estimated entityId
    print("download data...")
    create_path(args.output_path)
    ee = EarthExplorer(usr_pw['user'], usr_pw['password'])
    for scene in scenes:
        ee.download(identifier=scene['entity_id'], output_dir=args.output_path)
        # open_tarfile_function(path=args.output_path,
        #                       filename=os.path.join(args.output_path, scene['display_id'] + ".tar.gz"))

    ee.logout()


if __name__ == "__main__":
    download_data(args=getargs())

