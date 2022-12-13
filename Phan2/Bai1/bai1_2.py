import numpy as np
import rasterio
from rasterio.windows import Window


def ndvi(band_r, band_nir):
    return (band_nir - band_r)/(band_nir + band_r)

def prsi(band_r, band_green, band_nir):
    return (band_r - band_green)/band_nir

def savi(band_r, band_nir):
    return (1.5*(band_nir - band_r))/(band_nir + band_r + 0.5)


path_img = r"E:\Sassandra-Marahoue17-22-Jan-2022_Mosaic.tif"
out_ndvi = r"E:\ndvi.tif"
out_savi = r"E:\savi.tif"
out_prsi = r"E:\prsi.tif"

# lấy thông tin ảnh
with rasterio.open(path_img) as src:
    crs = src.crs
    tranf = src.transform
    height, width = src.height, src.width
    meta = src.meta


# tính ndvi, savi, prsi
meta.update({'dtype':'float64', 'count': 1})
crop_size = 2000
list_weight = list(range(0, width, crop_size))
list_hight = list(range(0, height, crop_size))[:-1]
crop_h = crop_size
crop_w = crop_size

# output 3 chi so
with rasterio.open(out_ndvi, 'w', **meta) as output_ds:
        output_ds = np.empty((1, height, width))

with rasterio.open(out_ndvi, "r+") as output_ds:
    with rasterio.open(path_img) as src:
        for start_h_org in list_hight:
            for start_w_org in list_weight:
                if start_h_org % crop_size != 0:
                    crop_h = height - start_h_org
                elif start_w_org % crop_size != 0:
                    crop_w = width - start_w_org


                # print(start_h_org, start_w_org, crop_h, crop_w)
                img_win = src.read(window= Window(start_h_org, start_w_org, crop_h, crop_w))
                img_ndvi = ndvi(img_win[0], img_win[3])
                # img_prsi = prsi(img_win[0], img_win[1], img_win[3])
                # img_savi = savi(img_win[0], img_win[3])
                output_ds.write(img_ndvi, window = Window(start_h_org, start_w_org, crop_h, crop_w), indexes = 1)


