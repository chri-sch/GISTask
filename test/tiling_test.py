import os
from itertools import product
import rasterio as rio
from rasterio import windows

in_path = r'C:\_data\vexcel\orlando\fill'
input_filename = 'orlando_ortho-nir_bluesky-ultra1.tif'

out_path = r'C:\temp'
output_filename = 'tile_{}-{}.tif'


def get_tiles(ds, width=256, height=256):
    nols, nrows = ds.meta['width'], ds.meta['height']
    offsets = product(range(0, nols, width), range(0, nrows, height))
    big_window = windows.Window(col_off=0, row_off=0, width=nols, height=nrows)
    for col_off, row_off in offsets:
        window = windows.Window(col_off=col_off, row_off=row_off, width=width, height=height).intersection(big_window)
        transform = windows.transform(window, ds.transform)
        yield window, transform


with rio.open(os.path.join(in_path, input_filename)) as inds:
    tile_width, tile_height = 70000, 70000

    meta = inds.meta.copy()
    meta.update(compress='deflate')
    # meta.update(BIGTIFF="IF_SAFER")

    for window, transform in get_tiles(inds, width=tile_width, height=tile_height):
        print(window)
        meta['transform'] = transform
        meta['width'], meta['height'] = window.width, window.height
        outpath = os.path.join(out_path, output_filename.format(int(window.col_off), int(window.row_off)))
        with rio.open(outpath, 'w', **meta, BIGTIFF='YES') as outds:
            outds.write(inds.read(window=window))
