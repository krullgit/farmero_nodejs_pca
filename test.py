import ee
#from IPython.display import Image
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import re
import sys
import json

import fiona
from PIL import Image
import rasterio
import rasterio.mask
from osgeo import gdal


########### FUNCTIONS ############

def clipTIF(tifNVDI, clippedTifNVDI, coord):
    #geoms = [{'type': 'Polygon', 'coordinates': [[(13.272943496704102, 52.26377127581493),(13.275260925292969, 52.25586469803543),(13.288092613220215, 52.2596999583217),(13.292684555053711, 52.26650278898101),(13.296761512756348,52.27017956020817),(13.296289443969727,52.27123001026625),(13.288435935974121,52.26933918223966),(13.28174114227295,52.26834121271067),(13.272943496704102,52.26377127581493)]]}]
    geoms = [{'type': 'Polygon', 'coordinates': [[tuple(l) for l in coord]] }]

    with rasterio.open(tifNVDI) as src:
        out_image, out_transform = rasterio.mask.mask(src, geoms, crop=True)
        out_meta = src.meta


    out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform})

    with rasterio.open(clippedTifNVDI, "w", **out_meta) as dest:
        dest.write(out_image)

def safeTIF(tif, clippedTif):

    with rasterio.open(tif) as src:
        out_image = src
        out_meta = src.meta

    out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2]})

    with rasterio.open(clippedTif, "w", **out_meta) as dest:
        dest.write(out_image)


# FUNC 

def polygonToZIPfromEE(polygon, dayStart, dayEnd, band):
    collection = (ee.ImageCollection('COPERNICUS/S2')
        .filterDate(dayStart, dayEnd)
        .filterBounds(polygon)
        .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 30)
        .map(maskS2clouds))

    if(band == 'NVDI'):
        image1 = collection.mean().normalizedDifference(['B5', 'B4'])
    if(band == 'RGB'):
        image1 = collection.sort('CLOUD_COVER').first();

    path = image1.getDownloadUrl({
        'scale': 10, 
        'crs': 'EPSG:4326',
        'region': coord
    })

    print(path)

    return urlopen(path)

# FUNC
def extractTIFFromZIP(resp, regex):
    with ZipFile(BytesIO(resp.read())) as my_zip_file:
        for contained_file in my_zip_file.namelist():
            if(re.compile("(.*)"+regex).match(contained_file)):
                print(contained_file)
                return my_zip_file.open(contained_file)
            #else:
            
            # with open(("unzipped_and_read_" + contained_file + ".file"), "wb") as output:
            #for line in my_zip_file.open(contained_file).readlines():
                #print(line)
                # output.write(line)

def extractTIFFromZIPToFile(resp, regex):
    with ZipFile(BytesIO(resp.read())) as my_zip_file:
        my_zip_file.extractall()
        for contained_file in my_zip_file.namelist():
            if(re.compile("(.*)"+regex).match(contained_file)):
                print(contained_file)
                my_zip_file.extract(contained_file, 'data/')
                return contained_file

# FUNC
def maskS2clouds(image):
    qa = image.select('QA60')
    # Bits 10 and 11 are clouds and cirrus, respectively.
    cloudBitMask = 1 << 10;
    cirrusBitMask = 1 << 11;
    # Both flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloudBitMask).eq(0) and(
        qa.bitwiseAnd(cirrusBitMask).eq(0))

    # Return the masked and scaled data, without the QA bands.
    return image.updateMask(mask).divide(10000).select("B.*").copyProperties(image, ["system:time_start"])

# FUNC
def makeRGB(file_list, outName):
    # Read metadata of first file
    with rasterio.open(file_list[0]) as src0:
        meta = src0.meta

    # Update meta to reflect the number of layers
    meta.update(count = len(file_list))

    # Read each layer and write it to stack
    with rasterio.open(outName, 'w', **meta) as dst:
        for id, layer in enumerate(file_list, start=1):
            with rasterio.open(layer) as src1:
                dst.write_band(id, src1.read(1))

# FUNC
def tifToJPG(inPath, outPath):
    options_list = [
        '-ot Byte',
        '-of JPEG',
        '-scale'
    ] 
    options_string = " ".join(options_list)
    gdal.Translate(outPath,
                inPath,
            options=options_string)

# FUNC
def tifToPNG(inPath, outPath):
    options_list = [
        '-ot Byte',
        '-of PNG',
        '-b 3',
        '-b 2',
        '-b 1',
        '-scale'
    ] 
    options_string = " ".join(options_list)
    gdal.Translate(outPath,
                inPath,
            options=options_string)


# FUNC
def clipBlackPixels(inPath, outPath):
    img = Image.open(inPath)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] < 100 and item[1] < 100 and item[2] < 100:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(outPath, "PNG")


# FUNC
def mergeTwoimages(imageOnePath, imageTwoPath, fieldAndChange):
    background = Image.open(imageOnePath)
    foreground = Image.open(imageTwoPath)

    background.paste(foreground, (0, 0), foreground)
    background.save(fieldAndChange, "PNG")

# FUNC
def writeToFile(zipRGBDay2, zipRGBDay2FileName):
    with open(zipRGBDay2FileName, 'w') as the_file:
        the_file.write(zipRGBDay2)




########### MAIN ############

# Earth Enigine Initialize
ee.Initialize()

# PARAM
# This is when running without the nodejs server
#coordString = "[[13.272943496704102, 52.26377127581493],[13.275260925292969, 52.25586469803543],[13.288092613220215, 52.2596999583217],[13.292684555053711, 52.26650278898101],[13.296761512756348,52.27017956020817],[13.296289443969727,52.27123001026625],[13.288435935974121,52.26933918223966],[13.28174114227295,52.26834121271067],[13.272943496704102,52.26377127581493]]"
#coord = json.loads(coordString) 
# In this case the nodejs server provides the coordinates in an argument
coord = json.loads(sys.argv[1])
polygon = ee.Geometry.Polygon([coord])
dayStartDay1 = '2018-07-03'
dayEndDay1 = '2018-07-04'
dayStartDay2 = '2018-07-31'
dayEndDay2 = '2018-08-01'
zipRGBDay2FileName = 'data/zipRGBDay2FileName.zip' 
#DO
zipNVDIDay1 = polygonToZIPfromEE(polygon, dayStartDay1, dayEndDay1, 'NVDI')
zipNVDIDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'NVDI') 
zipRGBDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'RGB')
#writeToFile(zipRGBDay2, zipRGBDay2FileName)
tifNVDIDay1 = extractTIFFromZIP(zipNVDIDay1, '.tif')
tifNVDIDay2 = extractTIFFromZIP(zipNVDIDay2, '.tif')

print('1')
zipRGBDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'RGB')
tifRedDay2 = extractTIFFromZIPToFile(zipRGBDay2, 'B2.tif')

print('2')
zipRGBDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'RGB')
tifGreenDay2 = extractTIFFromZIPToFile(zipRGBDay2, 'B3.tif')

print('3')
zipRGBDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'RGB')
tifBlueDay2 = extractTIFFromZIPToFile(zipRGBDay2, 'B4.tif')

# PARAMS
coord = coord # in 
tifNVDIDay1 = tifNVDIDay1 # in
tifNVDIDay2 = tifNVDIDay2 # in
tifRedDay2 = tifRedDay2 # in #TODO safe this in a file
tifGreenDay2 = tifGreenDay2 # in #TODO safe this in a file
tifBlueDay2 = tifBlueDay2 # in #TODO safe this in a file
clippedTifNVDIDay1 = 'data/nvdiDay1.tif' # out 
clippedTifNVDIDay2 = 'data/nvdiDay2.tif' # out 
clippedJpgNVDIDay1 = 'data/nvdiDay1.jpg' # out 
clippedJpgNVDIDay2 = 'data/nvdiDay2.jpg' # out 
pngRedDay2 = 'data/redDay2.png' # out 
pngGreenDay2 = 'data/greenDay2.png' # out 
pngBlueDay2 = 'data/blueDay2.png' # out 
# DO
clipTIF(tifNVDIDay1, clippedTifNVDIDay1, coord)
clipTIF(tifNVDIDay2, clippedTifNVDIDay2, coord)
tifToJPG(clippedTifNVDIDay1, clippedJpgNVDIDay1)
tifToJPG(clippedTifNVDIDay2, clippedJpgNVDIDay2)
#tifToPNG(tifRedDay2, pngRedDay2)
#tifToPNG(tifGreenDay2, pngGreenDay2)
#tifToPNG(tifBlueDay2, pngBlueDay2)

# PARAM
pngRedDay2 = pngRedDay2 # in
pngGreenDay2 = pngGreenDay2 # in
pngBlueDay2 = pngBlueDay2 # in
file_list = [tifRedDay2, tifGreenDay2, tifBlueDay2] # TODO these are memory tiffs but need to be filenames
tifImage = 'data/stack.tif' # out
# DO
makeRGB(file_list, tifImage) # produces 1 combined geotif out of 3 geotifs (r,g,b)

# PARAM
tifImage = tifImage # in
pngImage = 'data/stack.png'# out
# DO
tifToPNG(tifImage, pngImage) # converts geotif to jpg

print("finish producing Images")

# # TODO
# # 1. Images have to be processed by the PCA instead of hardcoding them like below

# # PARAM
# nameOfChangemap = 'data/cleanchangemap.jpg' # in
# nameOfChangemapTransparent = 'data/cleanchangemapTransparent.png' # out
# # DO
# clipBlackPixels(nameOfChangemap, nameOfChangemapTransparent) # clips the black pixels (no change in field)

# # PARAM
# pngImage = pngImage # in
# nameOfChangemapTransparent = nameOfChangemapTransparent # in
# fieldAndChange = 'data/fieldAndChange.png' # out
# # DO
# mergeTwoimages(pngImage, nameOfChangemapTransparent, fieldAndChange) # merges the rgb image and the changemap image to show critical areas on the field

# # show field with critical areas
# print(fieldAndChange)


# #print("out2.jpg")


########################## PCA ################################


# import cv2
# import numpy as np
# from sklearn.cluster import KMeans
# from sklearn.decomposition import PCA
# from collections import Counter
# from scipy.misc import imread, imresize, imsave
# from skimage import io

# def find_vector_set(diff_image, new_size):
   
#     i = 0
#     j = 0
#     vector_set = np.zeros((((new_size[0] * new_size[1]) / 25).astype(np.int), 25))
#     while i < vector_set.shape[0]:
#         while j < new_size[0]:
#             k = 0
#             while k < new_size[1]:
#                 block   = diff_image[j:j+5, k:k+5]
#                 feature = block.ravel()
#                 vector_set[i, :] = feature
#                 k = k + 5
#             j = j + 5
#         i = i + 1
        
            
#     mean_vec   = np.mean(vector_set, axis = 0)    
#     vector_set = vector_set - mean_vec
    
#     return vector_set, mean_vec
    
  
# def find_FVS(EVS, diff_image, mean_vec, new):
    
#     i = 2 
#     feature_vector_set = []
    
#     while i < new[0] - 2:
#         j = 2
#         while j < new[1] - 2:
#             block = diff_image[i-2:i+3, j-2:j+3]
#             feature = block.flatten()
#             feature_vector_set.append(feature)
#             j = j+1
#         i = i+1
        
#     FVS = np.dot(feature_vector_set, EVS)
#     FVS = FVS - mean_vec
#     return FVS

# def clustering(FVS, components, new):
    
#     kmeans = KMeans(components, verbose = 0)
#     kmeans.fit(FVS)
#     output = kmeans.predict(FVS)
#     count  = Counter(output)

#     least_index = min(count, key = count.get)            
#     change_map  = np.reshape(output.astype(np.int),((new[0] - 4).astype(np.int), (new[1] - 4).astype(np.int)))
    
#     return least_index, change_map

   
# def find_PCAKmeans(imagepath1, imagepath2):
    
    
#     image1_pre = io.imread(imagepath1, as_gray=True)
#     image2_pre = io.imread(imagepath2, as_gray=True)
    
#     image1 = image1_pre[:, :]
#     image2 = image2_pre[:, :]
    
#     new_size = np.asarray(image1.shape) / 5 * 5
#     image1 = imresize(image1, (new_size)).astype(np.int16)
#     image2 = imresize(image2, (new_size)).astype(np.int16)
    
#     diff_image = abs(image1 - image2)   
#     imsave('diff.jpg', diff_image)
        
#     vector_set, mean_vec = find_vector_set(diff_image, new_size)
    
#     pca     = PCA()
#     pca.fit(vector_set)
#     EVS = pca.components_
        
#     FVS     = find_FVS(EVS, diff_image, mean_vec, new_size)
    
    
#     components = 3
#     least_index, change_map = clustering(FVS, components, new_size)
    
#     change_map[change_map == least_index] = 255
#     change_map[change_map != 255] = 0
    
#     change_map = change_map.astype(np.uint8)
#     kernel     = np.asarray(((0,0,1,0,0),
#                              (0,1,1,1,0),
#                              (1,1,1,1,1),
#                              (0,1,1,1,0),
#                              (0,0,1,0,0)), dtype=np.uint8)
#     cleanChangeMap = cv2.erode(change_map,kernel)
#     imsave("changemap.jpg", change_map)
#     imsave("cleanchangemap.jpg", cleanChangeMap)
#     print('cleanchangemap.jpg')

    
# if __name__ == "__main__":
#     #a = 'Andasol_09051987.jpg'
#     #b = 'Andasol_09122013.jpg'
#     a = 'testdata/f1.jpg'
#     b = 'testdata/f2.jpg'
#     find_PCAKmeans(a,b)    


