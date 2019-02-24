

######################### PCA ################################


import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import Counter
from scipy.misc import imread, imresize, imsave
from skimage import io

def find_vector_set(diff_image, new_size):
   
    i = 0
    j = 0
    vector_set = np.zeros((((new_size[0] * new_size[1]) / 25).astype(np.int), 25))
    while i < vector_set.shape[0]:
        while j < new_size[0]:
            k = 0
            while k < new_size[1]:
                block   = diff_image[j:j+5, k:k+5]
                feature = block.ravel()
                vector_set[i, :] = feature
                k = k + 5
            j = j + 5
        i = i + 1
        
            
    mean_vec   = np.mean(vector_set, axis = 0)    
    vector_set = vector_set - mean_vec
    
    return vector_set, mean_vec
    
  
def find_FVS(EVS, diff_image, mean_vec, new):
    
    i = 2 
    feature_vector_set = []
    
    while i < new[0] - 2:
        j = 2
        while j < new[1] - 2:
            block = diff_image[i-2:i+3, j-2:j+3]
            feature = block.flatten()
            feature_vector_set.append(feature)
            j = j+1
        i = i+1
        
    FVS = np.dot(feature_vector_set, EVS)
    FVS = FVS - mean_vec
    return FVS

def clustering(FVS, components, new):
    
    kmeans = KMeans(components, verbose = 0)
    kmeans.fit(FVS)
    output = kmeans.predict(FVS)
    count  = Counter(output)

    least_index = min(count, key = count.get)            
    change_map  = np.reshape(output.astype(np.int),((new[0] - 4).astype(np.int), (new[1] - 4).astype(np.int)))
    
    return least_index, change_map

   
def find_PCAKmeans(imagepath1, imagepath2):
    
    
    image1_pre = io.imread(imagepath1, as_gray=True)
    image2_pre = io.imread(imagepath2, as_gray=True)
    
    image1 = image1_pre[:, :]
    image2 = image2_pre[:, :]
    
    new_size = np.asarray(image1.shape) / 5 * 5
    image1 = imresize(image1, (new_size)).astype(np.int16)
    image2 = imresize(image2, (new_size)).astype(np.int16)
    
    diff_image = abs(image1 - image2)   
    imsave('diff.jpg', diff_image)
        
    vector_set, mean_vec = find_vector_set(diff_image, new_size)
    
    pca     = PCA()
    pca.fit(vector_set)
    EVS = pca.components_
        
    FVS     = find_FVS(EVS, diff_image, mean_vec, new_size)
    
    
    components = 3
    least_index, change_map = clustering(FVS, components, new_size)
    
    change_map[change_map == least_index] = 255
    change_map[change_map != 255] = 0
    
    change_map = change_map.astype(np.uint8)
    kernel     = np.asarray(((0,0,1,0,0),
                             (0,1,1,1,0),
                             (1,1,1,1,1),
                             (0,1,1,1,0),
                             (0,0,1,0,0)), dtype=np.uint8)
    cleanChangeMap = cv2.erode(change_map,kernel)
    imsave("changemap.jpg", change_map)
    imsave("cleanchangemap.jpg", cleanChangeMap)
    print('cleanchangemap.jpg')

    
if __name__ == "__main__":

    ##### WORKS #####
    #a = 'testdata/field1.jpg'
    #b = 'testdata/field2.jpg'

    ##### DOESNT WORK #####
    a = 'testdata/f1.jpg'
    b = 'testdata/f2.jpg'

    find_PCAKmeans(a,b)    