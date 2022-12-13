from osgeo import gdal, ogr, osr
from pyproj import Proj, transform
import glob, os
import sys
from multiprocessing.pool import Pool
from functools import partial
import multiprocessing
import time

from shapely.geometry import Polygon
from osgeo import ogr
import shapely.wkt
from shapely.geometry.multipolygon import MultiPolygon
from tqdm import *
foder_image = os.path.abspath(sys.argv[1])
shape_path = os.path.abspath(sys.argv[2])
foder_name = os.path.basename(foder_image)
parent = os.path.dirname(foder_image)
core = multiprocessing.cpu_count()


def load_shapefile(shape_path):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shape_path, 0)
    layer_in = dataSource.GetLayer()
    srs = layer_in.GetSpatialRef()
    geom_type = layer_in.GetGeomType()
    epsr1 =  srs.GetAttrValue('AUTHORITY',1)
    geom_type = layer_in.GetGeomType()
    layer_defn = layer_in.GetLayerDefn()
    list_polygon = []
    for feature in layer_in:
        geom =feature.GetGeometryRef()
        if geom is not None:
            if (geom.GetGeometryName()) == "POLYGON":
                shape_obj = (shapely.wkt.loads(geom.ExportToWkt()))
                polygon = (tuple(shape_obj.exterior.coords))
                poly_rs = []
                for point in polygon:
                    poly_rs.append((point[0],point[1]))
                poly_rs = tuple(poly_rs) 
                if len(poly_rs)>1:  
                    list_polygon.append(Polygon(poly_rs))
            elif (geom.GetGeometryName()) == "MULTIPOLYGON":
                for geo1 in geom:
                    if geo1 is not None:
                        shape_obj = (shapely.wkt.loads(geo1.ExportToWkt()))
                        polygon1 = (tuple(shape_obj.exterior.coords))
                        poly_rs = []
                        for point in polygon1:
                            poly_rs.append((point[0],point[1]))
                        poly_rs = tuple(poly_rs)
                        if len(poly_rs)>1:
                            list_polygon.append(Polygon(poly_rs))
    mul = MultiPolygon(list_polygon)
    for geom in mul:
        if not(geom.is_valid):
            print(1)

    result = MultiPolygon([geom if geom.is_valid else geom.buffer(0) for geom in mul])
    return result,epsr1,srs,geom_type



def polygon_to_geopolygon(polygon, geotransform):
    temp_geopolygon = []
    for point in polygon:
        geopoint = point_to_geopoint(point, geotransform)
        temp_geopolygon.append(geopoint)
    geopolygon = tuple(temp_geopolygon)
    return geopolygon


def point_to_geopoint(point, geotransform):
    topleftX = geotransform[0]
    topleftY = geotransform[3]
    XRes = geotransform[1]
    YRes = geotransform[5]
    geopoint = (topleftX + point[0] * XRes, topleftY + point[1] * YRes)
    return geopoint


def load_image_geom(image_path,epsr1):
    dataset_image = gdal.Open(image_path)
    w,h = dataset_image.RasterXSize,dataset_image.RasterYSize
    polygon = ((0,0),(w,0),(w,h),(0,h),(0,0))
    geotransform = dataset_image.GetGeoTransform()
    geopolygon = polygon_to_geopolygon(polygon,geotransform)
    proj = osr.SpatialReference(wkt=dataset_image.GetProjection())
    epsr2 = (proj.GetAttrValue('AUTHORITY',1))
    epsr1 = epsr2
    inProj = Proj(init='epsg:%s'%(epsr2))
    outProj = Proj(init='epsg:%s'%(epsr1))
    list_point = []
    for point in geopolygon:
        long,lat = point[0],point[1]
        x,y = transform(inProj,outProj,long,lat)
        list_point.append((x,y))
    return Polygon(tuple(list_point))


def create_list_id(path):
    list_id = []
    os.chdir(path)
    for file in glob.glob("*.tif"):
        list_id.append(file[:-4])
    return list_id


def crop_shape_pool(id_image,epsr1,result,path_shape_crop,shape_path):
    result2 = load_image_geom(os.path.join(foder_image,id_image+'.tif'),epsr1)
    dataset = gdal.Open(os.path.join(foder_image,id_image+'.tif'))
    srs = osr.SpatialReference(dataset.GetProjectionRef())
    a = [(geom.intersection(result2)) if geom.is_valid else (geom.buffer(0).intersection(result2)) for geom in result]
    b = [aa for aa in a if aa.geom_type == 'Polygon' ]
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds_out = driver.CreateDataSource(os.path.join(path_shape_crop,id_image+'.shp'))
    layer_out = ds_out.CreateLayer("Building area", srs = srs, geom_type = ogr.wkbPolygon)
    layer_defn = layer_out.GetLayerDefn()
    for polygon in b:
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for point in polygon.exterior.coords:
            ring.AddPoint(point[0], point[1])
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        outFeature = ogr.Feature(layer_defn)
        outFeature.SetGeometry(poly)
        layer_out.CreateFeature(outFeature)
    outFeature = None
    outLayer = None
    data_source = None
    return True


def crop_shape2():
    result, epsr1, srs, geom_type = load_shapefile(shape_path)
    list_id = create_list_id(foder_image)
    if not os.path.exists(os.path.join(parent,foder_name+'_shape')):
        os.makedirs(os.path.join(parent,foder_name+'_shape'))
    path_shape_crop = os.path.join(parent,foder_name+'_shape')
    p_cropshape = Pool(processes=core)
    pool_result = p_cropshape.imap_unordered(partial(crop_shape_pool,epsr1=epsr1,result=result,path_shape_crop=path_shape_crop,shape_path=shape_path), list_id)
    with tqdm(total=len(list_id)) as pbar:
        for i,_ in tqdm(enumerate(pool_result)):
            pbar.update()
    p_cropshape.close()
    p_cropshape.join()

if __name__ == "__main__":
    x1 = time.time()
    crop_shape2()
    print(time.time() - x1, "second")