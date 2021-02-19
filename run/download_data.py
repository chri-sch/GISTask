import landsatxplore.api
from landsatxplore.earthexplorer import EarthExplorer
import os
from helperFunctions.gen_functions import open_tarfile_function, getargs


def download_data(args):

    # set user and password of your account
    usr_pw = {'user': args.user, 'password': args.pwd}

    # Initialize a new API instance and get an access key
    api = landsatxplore.api.API(usr_pw['user'], usr_pw['password'])

    # Finding scenes for Graz (47.069888, 15.437851)
    scenes = api.search(
        dataset='LANDSAT_8_C1',
        latitude=47.069888,
        longitude=15.437851,
        start_date='2019-10-01',
        end_date='2019-10-30')

    print('{} scenes found.'.format(len(scenes)))
    api.logout()

    # download data from earth explorer by estimated entityId
    print("download data...")
    ee = EarthExplorer(usr_pw['user'], usr_pw['password'])
    for scene in scenes:
        ee.download(scene_id=scene['entityId'], output_dir=args.output_path)
        open_tarfile_function(path=args.output_path,
                              filename=os.path.join(args.output_path, scene['displayId'] + ".tar.gz"))

    ee.logout()


if __name__ == "__main__":
    download_data(args=getargs())

