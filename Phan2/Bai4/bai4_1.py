import cv2, glob, os
import numpy as np
import rasterio


def opening(mask, size_kernel=3):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(size_kernel,size_kernel))
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


def remove_area_small(mask, area_maximum):
    contours, _ = cv2.findContours(mask,cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area <= area_maximum:
            cv2.fillPoly(mask, [contour], 1)
    return mask


def main(dir_in, dir_out, area_maximum):
    os.makedirs(dir_out, exist_ok=True)
    for img_path in glob.glob(os.path.join(dir_in, '*.tif')):
        base_name = os.path.basename(img_path)
        out_img_path = os.path.join(dir_out, base_name)

        with rasterio.open(img_path) as src:
            img = src.read()
            meta = src.meta
        img = opening(img[0], size_kernel=3)
        img = remove_area_small(img, area_maximum)
        with rasterio.open(out_img_path, 'w', **meta) as dst:
            dst.write(np.array([img]))


if __name__ == '__main__':
    area_maximum = 30
    dir_in = r"E:\mmm\phan2\bai4\train_images_rs_512"
    dir_out = r"E:\mmm\phan2\bai4\train_images_rs_512_mo"
    main(dir_in, dir_out, area_maximum)

    


