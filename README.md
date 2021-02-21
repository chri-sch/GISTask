# GISTask

## Description

### The GISTask package enables the automatic download of remote sensing images, OSM buildings and uses the building layer for the automatic masking of the remote sensing images.

## Quick Start


Automatic masking of Landsat 7 ETM scenes between 2002-10-01 and 2003-10-30 with a maximum cloud cover of "6" based on OSM buildings with height attribute.

run_process.py --user user --pwd password --dataset LANDSAT_ETM_C1 --max_cloud_cover 6 –-start_date 2002-10-01 -–end_date 2003-10-30

The searching and downloading of remote sensing data is based on the landsatxplore Python package (https://github.com/yannforget/landsatxplore) which provides an interface to the EarthExplorer portal(http://earthexplorer.usgs.gov/).
To use the package, Earth Explorer credentials are required.

The OpenStreetMap buildings layer is downloaded based on the OSMnx (https://github.com/gboeing/osmnx) package.

Use the argument “-h” to get information about more options that can be passed to the application.

For using QGIS in Pycharm please identify your Qgis and Pycharm paths and modify them in the "pycharm.bat" file. Double clicking it will set the environmental variables correctly open up PyCharm automatically.


