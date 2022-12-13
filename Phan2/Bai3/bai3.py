import os
import rasterio
import numpy as np
import geopandas as gpd
import rasterio.features


def create_mask_with_class(out_path_mask, img_path, shp_path):
    with rasterio.open(img_path) as src:
        meta = src.meta
        height, width = src.height, src.width
        tr = src.transform
        crs_img = src.crs
    meta.update({   
        'count': 1, 
        'nodata': 0,
        'dtype': 'uint8'
        })

    df_shape = gpd.read_file(shp_path)
    if df_shape.crs.to_string() != crs_img.to_string():
        df_shape = df_shape.to_crs(epsg=str(crs_img.to_epsg()))
    
    i = 0
    for class_name in ['Building Demolition', 'Existing Building Extension', 'New Building', 'Other change', 'Rooftop Change', 'Vegetation Change']:
        i+=1
        df_shape.loc[df_shape['Chng_Type'] == class_name, 'valu']= i

    shapes = df_shape[['geometry', 'valu']]
    shapes = list(map(tuple, shapes.values))
    mask = rasterio.features.rasterize(shapes, out_shape=(height, width), transform=tr)
    with rasterio.open(out_path_mask, 'w', **meta) as dst:
            dst.write(np.array([mask]).astype('uint8'))
    print(f'\nDone {os.path.basename(img_path)}')

if __name__=='__main__':
    img_path = r"E:\mmm\phan2\Bai3\Image_stack\data_change.tif"
    shp_path = r"E:\mmm\phan2\Bai3\All_shapefile\Training_Sample_V3.shp"
    out_dir = r"E:\mmm\phan2\Bai3\Image_stack\data_change"
    os.makedirs(out_dir, exist_ok=True)
    out_path_mask = os.path.join(out_dir, os.path.basename(shp_path).replace('.shp','.tif'))
    create_mask_with_class(out_path_mask, img_path, shp_path)