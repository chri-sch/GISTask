import up42
from helperFunctions.gen_functions import getargs
from sqlalchemy import create_engine
import psycopg2
import geopandas as gpd
import os
import sys


def download_up42_scenes(args):
    # read area of interests
    con = psycopg2.connect(database="labeling", user=args.user, password=args.pwd, host=args.host)
    sql = "select id, bounding_box from ml_ops.labeling_roi where id = 131"
    aoi = gpd.GeoDataFrame.from_postgis(sql, con, geom_col='bounding_box')

    quick_looks = False

    """
        up42 part
    """
    up42.authenticate(project_id="97007ccc-06b6-4b4b-954e-3a23b66160c9",
                      project_api_key="ZByxk4hF.PvJUgH8KtzLCAiYOHTIuyqoXb9rMqp3KFZB")

    # search scenes in aoi
    catalog = up42.initialize_catalog()

    search_parameters = catalog.construct_parameters(geometry=aoi,
                                                     start_date="2018-01-01",
                                                     end_date="2020-12-31",
                                                     sensors=["pleiades"],
                                                     # sensors=["spot"],
                                                     max_cloudcover=5,
                                                     sortby="cloudCoverage",
                                                     limit=50)

    search_results = catalog.search(search_parameters=search_parameters)

    # Download & visualize quicklooks
    if quick_looks:
        catalog.download_quicklooks(image_ids=search_results.id.to_list(), sensor="pleiades")
        catalog.map_quicklooks(scenes=search_results, aoi=aoi)

    # order data frame by cloud coverage and incidence angle
    search_results['incidenceAngle'] = search_results.providerProperties.apply(lambda x: x['incidenceAngle'])
    search_results['incidenceAngleAlongTrack'] = search_results.providerProperties.apply(
        lambda x: x['incidenceAngleAlongTrack'])
    search_results.sort_values(by=['cloudCoverage', 'incidenceAngle'], inplace=True)
    search_results = search_results.reset_index(drop=True)

    # convert list objects to string to be able to export dataframe as gpkg
    df = search_results.copy()
    df['blockNames'] = search_results['blockNames'].astype(str)
    df['up42:usageType'] = search_results['up42:usageType'].astype(str)
    df['providerProperties'] = search_results.providerProperties.astype(str)
    # df.to_file(os.path.join(args.output_path, "up42", "meta_scenes.gpkg"), layer="meta_scenes", driver="GPKG")
    print(f" Scene Id of selected scene: {search_results.loc[0].sceneId}")

    # create a new, empty up42 workflow and add a task
    project = up42.initialize_project()
    workflow = project.create_workflow(name="fetch-pleades-scene", use_existing=True)
    workflow.add_workflow_tasks(["Pléiades Display (Download)", "DIMAP -> GeoTIFF Conversion"])
    # workflow.add_workflow_tasks(["Pléiades Display (Download)"])

    # Define the workflow parameters and select which scene from the catalog search results to download.
    input_parameters = workflow.construct_parameters(geometry=aoi,
                                                     geometry_operation="bbox",
                                                     scene_ids=[search_results.loc[0].sceneId])
    # update parameters
    input_parameters['oneatlas-pleiades-display:1'].update({"max_cloud_cover": 5})

    # Estimate the price.
    estimate = workflow.estimate_job(input_parameters)

    # Run a test job to query data availability and check the configuration
    test_job = workflow.test_job(input_parameters=input_parameters, track_status=True)
    test_results = test_job.get_results_json()

    sys.exit(0)

    # Run the workflow as a job
    job = workflow.run_job(input_parameters, track_status=True)

    # Download & Visualize results.
    job.download_results(output_directory=os.path.join(args.output_path, "up42", "pleiades"))
    job.map_results(aoi=aoi)


if __name__ == "__main__":
    download_up42_scenes(args=getargs())
