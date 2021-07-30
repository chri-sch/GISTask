import pandas as pd
from helperFunctions.gen_functions import getargs
import os
from pyproj import Transformer

args = getargs()

# read coordinates to data frame
df = pd.read_csv(os.path.join(args.input_path, "fb_coordinates_UTM.csv"))

# get transformer based on epsg codes
transformer = Transformer.from_crs(32610, 4326)

lat, lon = transformer.transform(df.x, df.y)

df['lat'] = lat
df['long'] = lon

df.to_csv(os.path.join(args.input_path, "fb_coordinates_WGS84.csv"))

print()