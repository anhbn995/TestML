import rasterio
from rasterio.windows import Window

path_img = r"E:\Sassandra-Marahoue17-22-Jan-2022_Mosaic.tif"
# lấy thông tin ảnh
with rasterio.open(path_img) as src:
    crs = src.crs
    tranf = src.transform
    height, width = src.height, src.width
    # gt = src.affine
    # print('do phan giai', gt[0])
    