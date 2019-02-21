import ee
from IPython.display import Image
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import re
import sys
import json

import fiona
import rasterio
import rasterio.mask


#coordString = "[[13.26634342077773, 52.25399802922547],[13.28883106115859, 52.25967223411166],[13.294667547974996, 52.27049324176266],[13.26960498693984, 52.26308691491034]]"
#coord = json.loads(coordString)

coord = json.loads(sys.argv[1])


def extractTifFromZIP(resp):
    with ZipFile(BytesIO(resp.read())) as my_zip_file:
        for contained_file in my_zip_file.namelist():
            if(re.compile("(.*).tif").match(contained_file)):
                return my_zip_file.open(contained_file)
            #else:
            
            # with open(("unzipped_and_read_" + contained_file + ".file"), "wb") as output:
            #for line in my_zip_file.open(contained_file).readlines():
                #print(line)
                # output.write(line)


ee.Initialize()

#polygon = ee.Geometry.Polygon([[[13.26634342077773, 52.25399802922547],[13.28883106115859, 52.25967223411166],[13.294667547974996, 52.27049324176266],[13.26960498693984, 52.26308691491034]]])
polygon = ee.Geometry.Polygon([coord])


collection = (ee.ImageCollection('COPERNICUS/S2')
    .filterDate('2018-07-30', '2018-09-8')
    .filterBounds(polygon))

image1 = collection.mean().normalizedDifference(['B5', 'B4'])

path = image1.getDownloadUrl({
    'scale': 10, 
    'crs': 'EPSG:4326',
    'region': coord
})

resp = urlopen(path)

tifFile = extractTifFromZIP(resp)

#geoms = [{'type': 'Polygon', 'coordinates': [[(13.272943496704102, 52.26377127581493),(13.275260925292969, 52.25586469803543),(13.288092613220215, 52.2596999583217),(13.292684555053711, 52.26650278898101),(13.296761512756348,52.27017956020817),(13.296289443969727,52.27123001026625),(13.288435935974121,52.26933918223966),(13.28174114227295,52.26834121271067),(13.272943496704102,52.26377127581493)]]}]
geoms = [{'type': 'Polygon', 'coordinates': [[tuple(l) for l in coord]] }]


with rasterio.open(tifFile) as src:
    out_image, out_transform = rasterio.mask.mask(src, geoms, crop=True)
    out_meta = src.meta


out_meta.update({"driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform})

with rasterio.open("out.tif", "w", **out_meta) as dest:
    dest.write(out_image)

from osgeo import gdal

options_list = [
    '-ot Byte',
    '-of JPEG',
    '-b 1',
    '-scale'
] 

options_string = " ".join(options_list)

gdal.Translate('out2.jpg',
            'out.tif',
            options=options_string)

print("out2.jpg")


