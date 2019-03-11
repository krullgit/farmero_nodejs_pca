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
from rasterio import plot


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

# FUNC

def polygonToZIPfromEE(polygon, dayStart, dayEnd, band):
    collection = (ee.ImageCollection('COPERNICUS/S2')
        .filterDate(dayStart, dayEnd)
        .filterBounds(polygon)
        .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 100)
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

    #return urlopen(path)
    return image1

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
        
# Accepts NDVI image and makes it look better using Rasterio plot
def colorndvi(imageinpath,imageoutpath):
    ndvi_img = rasterio.open(imageinpath)
    x = plot.show(ndvi_img)
    x.axis('off')
    fig = x.get_figure()
    fig.savefig(imageoutpath,transparent = True)



########### MAIN ############

# Earth Enigine Initialize
ee.Initialize()

# PARAM

# This is when running without the nodejs server


coordString = "[[12.941725850371768,51.57971352400993],[12.942047715453555,51.57588640768779],[12.940846085814883,51.571032040481654],[12.943442464141299,51.57112539858611],[12.944708466796328,51.570671943139885],[12.948763966826846,51.57088533450155],[12.949965596465518,51.57121875649885],[12.951789498595645,51.570325180040776],[12.954450249938418,51.57021848317042],[12.954471707610537,51.571432145293755],[12.946274876861025,51.580113552408065],[12.941725850371768,51.57971352400993]]"
#coordString = "[[14.566519260406494, 51.16942143993214],[14.571776390075684, 51.16933398636553],[14.57181930541992, 51.170383418219465],[14.57480192184448, 51.17024887700865],[14.57510232925415,51.17326923268294],[14.572194814682007,51.17347775773388],[14.571744203567503,51.17388135192782],[14.571443796157837,51.17345085132869],[14.568450450897215,51.17406296816258],[14.567999839782715,51.17329613919413],[14.56661581993103,51.17307416000739],[14.566519260406494,51.16942143993214]]"
#coordString = "[[13.272943496704102, 52.26377127581493],[13.275260925292969, 52.25586469803543],[13.288092613220215, 52.2596999583217],[13.292684555053711, 52.26650278898101],[13.296761512756348,52.27017956020817],[13.296289443969727,52.27123001026625],[13.288435935974121,52.26933918223966],[13.28174114227295,52.26834121271067],[13.272943496704102,52.26377127581493]]"
#coord = json.loads(coordString)
# In this case the nodejs server provides the coordinates in an argument
coord = json.loads(sys.argv[1])
polygon = ee.Geometry.Polygon([coord])
dayStartDay1 = '2018-07-03' # in
dayEndDay1 = '2018-07-04' # in
dayStartDay2 = '2018-07-29' # in
dayEndDay2 = '2018-08-01' # in

zipRGBDay2FileName = 'data/zipRGBDay2FileName.zip'
zipRGBDay1FileName = 'data/zipRGBDay1FileName.zip'
#DO
zipNVDIDay1 = polygonToZIPfromEE(polygon, dayStartDay1, dayEndDay1, 'NVDI')
zipNVDIDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'NVDI')

zipRGBDay1 = polygonToZIPfromEE(polygon, dayStartDay1, dayEndDay1, 'RGB')
zipRGBDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'RGB')

#changes made
#writeToFile(zipRGBDay1, zipRGBDay1FileName)
#writeToFile(zipRGBDay2, zipRGBDay2FileName)


tifNVDIDay1 = extractTIFFromZIP(zipNVDIDay1, '.tif')
tifNVDIDay2 = extractTIFFromZIP(zipNVDIDay2, '.tif')

print('1')
zipRGBDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'RGB')
tifRedDay2 = extractTIFFromZIPToFile(zipRGBDay2, 'B2.tif')
zipRGBDay1 = polygonToZIPfromEE(polygon, dayStartDay1, dayEndDay1, 'RGB')
tifRedDay1 = extractTIFFromZIPToFile(zipRGBDay1, 'B2.tif')

print('2')
zipRGBDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'RGB')
tifGreenDay2 = extractTIFFromZIPToFile(zipRGBDay2, 'B3.tif')
zipRGBDay1 = polygonToZIPfromEE(polygon, dayStartDay1, dayEndDay1, 'RGB')
tifGreenDay1 = extractTIFFromZIPToFile(zipRGBDay1, 'B3.tif')

print('3')
zipRGBDay2 = polygonToZIPfromEE(polygon, dayStartDay2, dayEndDay2, 'RGB')
tifBlueDay2 = extractTIFFromZIPToFile(zipRGBDay2, 'B4.tif')
zipRGBDay1 = polygonToZIPfromEE(polygon, dayStartDay1, dayEndDay1, 'RGB')
tifBlueDay1 = extractTIFFromZIPToFile(zipRGBDay1, 'B4.tif')

# PARAMS
coord = coord # in
tifNVDIDay1 = tifNVDIDay1 # in
tifNVDIDay2 = tifNVDIDay2 # in

tifRedDay2 = tifRedDay2 # in #TODO safe this in a file
tifGreenDay2 = tifGreenDay2 # in #TODO safe this in a file
tifBlueDay2 = tifBlueDay2 # in #TODO safe this in a file

tifRedDay1 = tifRedDay1 # in #TODO safe this in a file
tifGreenDay1 = tifGreenDay1 # in #TODO safe this in a file
tifBlueDay1 = tifBlueDay1 # in #TODO safe this in a file
clippedTifNVDIDay1 = 'data/nvdiDay1.tif' # out
clippedTifNVDIDay2 = 'data/nvdiDay2.tif' # out
clippedJpgNVDIDay1 = 'data/nvdiDay1.jpg' # out
clippedJpgNVDIDay2 = 'data/nvdiDay2.jpg' # out

clippedJpgNVDIDay1_color = 'data/nvdiDay1_color.png' # out
clippedJpgNVDIDay2_color = 'data/nvdiDay2_color.png' # out

pngRedDay2 = 'data/redDay2.png' # out
pngGreenDay2 = 'data/greenDay2.png' # out
pngBlueDay2 = 'data/blueDay2.png' # out

pngRedDay1 = 'data/redDay1.png' # out
pngGreenDay1 = 'data/greenDay1.png' # out
pngBlueDay1 = 'data/blueDay1.png' # out
# DO
clipTIF(tifNVDIDay1, clippedTifNVDIDay1, coord)
clipTIF(tifNVDIDay2, clippedTifNVDIDay2, coord)
tifToJPG(clippedTifNVDIDay1, clippedJpgNVDIDay1)
tifToJPG(clippedTifNVDIDay2, clippedJpgNVDIDay2)

#Make NDVI look much better
colorndvi(clippedJpgNVDIDay1,clippedJpgNVDIDay1_color)
colorndvi(clippedJpgNVDIDay2,clippedJpgNVDIDay2_color)

#tifToPNG(tifRedDay2, pngRedDay2)
#tifToPNG(tifGreenDay2, pngGreenDay2)
#tifToPNG(tifBlueDay2, pngBlueDay2)

# PARAM
pngRedDay2 = pngRedDay2 # in
pngGreenDay2 = pngGreenDay2 # in
pngBlueDay2 = pngBlueDay2 # in

pngRedDay1 = pngRedDay1 # in
pngGreenDay1 = pngGreenDay1 # in
pngBlueDay1 = pngBlueDay1 # in

file_list_day2 = [tifRedDay2, tifGreenDay2, tifBlueDay2] # TODO these are memory tiffs but need to be filenames
tifImage_day2 = 'data/stack_day2.tif' # out

file_list_day1 = [tifRedDay1, tifGreenDay1, tifBlueDay1] # TODO these are memory tiffs but need to be filenames
tifImage_day1 = 'data/stack_day1.tif' # out
# DO
makeRGB(file_list_day2, tifImage_day2) # produces 1 combined geotif out of 3 geotifs (r,g,b)
makeRGB(file_list_day1, tifImage_day1) # produces 1 combined geotif out of 3 geotifs (r,g,b)


# PARAM
tifImage_day2 = tifImage_day2 # in
pngImage_day2 = 'data/stack_day2.png'# out

tifImage_day1 = tifImage_day1 # in
pngImage_day1 = 'data/stack_day1.png'# out
# DO
tifToPNG(tifImage_day2, pngImage_day2) # converts geotif to jpg
tifToPNG(tifImage_day1, pngImage_day1) # converts geotif to jpg

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
