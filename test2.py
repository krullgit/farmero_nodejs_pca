import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import Counter
from skimage import io
import skimage
import imageio
from scipy.misc import imsave


def find_vector_set(diff_image, new_size):
   
    i = 0
    j = 0
    x = (new_size[0] * new_size[1])
    vector_set = np.zeros(((x / 25).astype(np.int), 25))
    print ("diff_image.shape" + str(diff_image.shape))

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
        
    print ('\nvector_set shape', vector_set.shape)
            
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
    print ("\nfeature vector space size", FVS.shape)
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
    
    print ('Operating')
    
    image1_pre = io.imread(imagepath1, as_gray=True)
    image2_pre = io.imread(imagepath2, as_gray=True)
        
    image1 = image1_pre[:, :]
    image2 = image2_pre[:, :]
    
    new_size = np.asarray(image1.shape) / 5 * 5

    image1 = skimage.transform.resize(image1, (new_size))
    image2 = skimage.transform.resize(image2, (new_size))
 
    diff_image = abs(image1 - image2)   
    imsave('diff.jpg', diff_image)
    print ('\nBoth images resized to ',new_size)
        
    vector_set, mean_vec = find_vector_set(diff_image, new_size)
    
    pca     = PCA()
    pca.fit(vector_set)
    EVS = pca.components_
        
    FVS     = find_FVS(EVS, diff_image, mean_vec, new_size)
    
    print ('\ncomputing k means')
    
    components = 10
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
    imageio.imwrite("changemap.jpg", change_map)
    imageio.imwrite("cleanchangemap.jpg", cleanChangeMap)

    
if __name__ == "__main__":
    #a = 'Andasol_09051987.jpg'
    #b = 'Andasol_09122013.jpg'
    a = 'testdata/field1.jpg'
    b = 'testdata/field2.jpg'
    find_PCAKmeans(a,b)    
    
    