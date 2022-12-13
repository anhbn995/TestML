import os, glob
import rasterio 
from osgeo import gdal
import numpy as np
import random
import cv2


INPUT_SIZE = 256
num_class = 4
def create_list_id(path):
    list_id = []
    os.chdir(path)
    types = ('*.png', '*.tif')
    for files in types:
        for file in glob.glob(files):
            list_id.append(file)        
    return list_id

def split_black_image(list_id, mask_dir, thres):
    negative_fn = []
    for fn in list_id:
        dataset = gdal.Open(os.path.join(mask_dir,fn))
        values = dataset.ReadAsArray()        
        h,w = values.shape[0:2]
        # print(values.shape)
        if np.count_nonzero((values==255).astype(np.uint8)) <= thres*h*w:
            negative_fn.append(fn)
    positive_fn = [id_image for id_image in list_id if id_image not in negative_fn]
    count = len(negative_fn)
    print("Black mask count: " + str(count) + "/" +str(len(list_id)))
    return positive_fn, negative_fn

def rotate_angle(org_matrix, angle):
    m1 = np.rot90(org_matrix)
    m2 = np.rot90(m1)
    m3 = np.rot90(m2)
    if angle == "90":
        return m1
    elif angle == "180":
        return m2
    elif angle == "270":
        return m3
def data_gen_not_batch(image_path, mask_path,list_id,augment=True,batch_size = 4):
    num = len(list_id)
    
    color = (0,0,0)
    INPUT_SIZE = 256
    while True:
        x = []
        y = []
        while len(x)<batch_size:
            idx = random.randint(0, num-1)
            im_name = list_id[idx]
            image_fn = os.path.join(image_path, im_name)
            mask_fn = os.path.join(mask_path, im_name)
            with rasterio.open(image_fn, 'r') as f1:
                width,height = f1.width,f1.height
                new_image_width = new_image_height = max(width,height)
                # if width < 512 and height < 512:
                values = f1.read().transpose(1,2,0)
                x_center = (new_image_width - width) // 2
                y_center = (new_image_height - height) // 2
                result = np.full((new_image_height,new_image_width, 3), color, dtype=np.uint8)
                result[y_center:y_center+height, x_center:x_center+width] = values
                result = cv2.resize(result,(INPUT_SIZE, INPUT_SIZE), interpolation = cv2.INTER_CUBIC)
                image = result/255.0
                with rasterio.open(mask_fn, 'r') as f:
                    mask = f.read().astype(np.uint8)
                    mask = np.array((mask[0]==255).astype(np.uint8))
                    result_mask = np.full((new_image_height,new_image_width), 0, dtype=np.uint8)
                    result_mask[y_center:y_center+height, x_center:x_center+width] = mask
                    result_mask = cv2.resize(result_mask,(INPUT_SIZE, INPUT_SIZE), interpolation = cv2.INTER_CUBIC).astype(np.uint8)
                    mask = np.expand_dims(result_mask,axis = -1)
                    if augment:
                    # logging.warning("'augment' is depricated. Use 'augmentation' instead.")
                        if random.randint(0, 1):
                            aug_index1 = random.randint(0, 2)
                            if aug_index1 == 0:
                                image = np.fliplr(image)
                                mask = np.fliplr(mask)
                            elif aug_index1 == 1:
                                image = np.flipud(image)
                                mask = np.flipud(mask)
                            aug_index2 = random.randint(0, 3)
                            if aug_index2 == 0:
                                image = rotate_angle(image, "90")
                                mask = rotate_angle(mask, "90")
                            elif aug_index2 == 1:
                                image = rotate_angle(image, "180")
                                mask = rotate_angle(mask, "180")
                            elif aug_index2 == 2:
                                image = rotate_angle(image, "270")
                                mask = rotate_angle(mask, "270")
                    x.append(image)
                    y.append(mask)
        yield np.array(x), np.array(y)


            
        
def data_gen(positive_fn, negative_fn, image_path, mask_path, batch_size, scale_neg,num_chanel,num_class,augment=None):
    while True:
        if len(negative_fn) >0:
            index_neg=np.random.choice(len(negative_fn),int(len(positive_fn)*scale_neg))
            list_neg_train = [negative_fn[idx] for idx in index_neg]
        else :
            list_neg_train=[]
        list_id_gen = [idx for idx in positive_fn]
        list_id_gen.extend(list_neg_train)
        np.random.shuffle(list_id_gen)
        indx= np.random.choice(len(list_id_gen),batch_size)                         
        x = []
        y = []
        gen_id = []
        for idx in indx: 
            im_name = list_id_gen[idx]         
            image = get_x(im_name,image_path, num_chanel)
            mask = get_y(im_name,mask_path,num_class)

            if augment:
                if random.randint(0, 1):
                    aug_index1 = random.randint(0, 2)
                    if aug_index1 == 0:
                        image = np.fliplr(image)
                        mask = np.fliplr(mask)
                    elif aug_index1 == 1:
                        image = np.flipud(image)
                        mask = np.flipud(mask)
                    aug_index2 = random.randint(0, 3)
                    if aug_index2 == 0:
                        image = rotate_angle(image, "90")
                        mask = rotate_angle(mask, "90")
                    elif aug_index2 == 1:
                        image = rotate_angle(image, "180")
                        mask = rotate_angle(mask, "180")
                    elif aug_index2 == 2:
                        image = rotate_angle(image, "270")
                        mask = rotate_angle(mask, "270")
                    
            gen_id.append(im_name)
            x.append(image)
            y.append(mask)         
        yield np.array(x), np.array(y)

def get_x(im_name,img_path,num_chanel):
    fn = os.path.join(img_path, im_name)
    dataset = gdal.Open(fn)
    values = dataset.ReadAsArray()
    result = []
    for chan_i in range(num_chanel):
        result.append(cv2.resize(values[chan_i],(INPUT_SIZE, INPUT_SIZE), interpolation = cv2.INTER_CUBIC))
    del values
    result = np.array(result).astype(np.float32)
    return result.swapaxes(0,1).swapaxes(1,2)/255.0

def get_y(im_name,mask_path,num_class):   
    y_file = os.path.join(mask_path, im_name)
    with rasterio.open(y_file, 'r') as f:
        values = f.read().astype(np.uint8)
    result = []
    if num_class > 3:
        for chan_i in range(num_class):  
            result.append((cv2.resize((values[chan_i]==255).astype(np.uint8),(INPUT_SIZE, INPUT_SIZE), interpolation = cv2.INTER_CUBIC)>0.5).astype(np.uint8))
        mask_all = np.stack(result,axis=-1)
    elif num_class==2:
        mask = np.array((values[0]==255).astype(np.uint8))
        mask2 = np.array((cv2.bitwise_not(values[0])==255).astype(np.uint8))
        mask = cv2.resize(mask,(INPUT_SIZE, INPUT_SIZE), interpolation = cv2.INTER_CUBIC).astype(np.uint8)
        mask2 = cv2.resize(mask2,(INPUT_SIZE, INPUT_SIZE), interpolation = cv2.INTER_CUBIC).astype(np.uint8)
        result.append(mask2)
        result.append(mask)
        mask_all = np.stack(result,axis=-1)
    elif num_class==1:
        mask = np.array((values[0]==255).astype(np.uint8))
        mask_all = np.array((values[0]==255).astype(np.uint8))
        mask_all = np.expand_dims(mask_all,axis = -1)
    return np.array(mask_all).astype(np.uint8)