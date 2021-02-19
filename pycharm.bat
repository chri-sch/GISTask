

call "C:\Program Files\QGIS 3.12"\bin\o4w_env.bat"
call qt5_env.bat
call py3_env.bat

path C:\Program Files\QGIS 3.12\apps\qgis\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=C:\Program Files\QGIS 3.12\apps\qgis\qtplugins;C:\Program Files\QGIS 3.12\apps\qt5\plugins
start /d "C:\Users\chsc\AppData\Local\JetBrains\PyCharm Community Edition 2019.3.2\bin" pycharm64.exe
