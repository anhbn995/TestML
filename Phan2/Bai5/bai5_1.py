import os
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
from geopandas import GeoDataFrame

fp_in = r'E:\mmm\phan2\bai5\2019_green_cover.tif'
fp_out = r'E:\mmm\phan2\bai5\2019_green_cover.shp'
with rasterio.open(fp_in, 'r+') as dst:
    dst.nodata = 0
with rasterio.open(fp_in) as src:
    data = src.read(1, masked=True)
    shape_gen = ((shape(s), v) for s, v in shapes(data, transform=src.transform))
    gdf = GeoDataFrame(dict(zip(["geometry", "class"], zip(*shape_gen))), crs=src.crs)
gdf.to_file(fp_out)