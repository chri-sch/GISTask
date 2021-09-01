import pprint
import rasterio
from geojson import Feature, FeatureCollection, Polygon, dump
from rasterio import features

with rasterio.open(r'C:\Pycharm_Projects\GISTask\input\Edges_USA_SanFran_merged_4326 (1).tif') as src:
    lines = src.read(1)

mask = lines == 255
shapes = features.shapes(lines, mask=mask, transform=src.transform)

features = []
i = 0
for shape in shapes:
    Polygon(shape[0]['coordinates'])
    poly_geojson = Polygon(shape[0]['coordinates'])
    errors = poly_geojson.errors()
    if errors:
        print('Errors for{}'.format(errors))
    feature = Feature(geometry=poly_geojson, properties=dict(quadkey=i))
    features.append(feature)
    i += 1

feature_collection = FeatureCollection(features)

with open("output.geojson", 'w') as f:
    dump(feature_collection, f)

