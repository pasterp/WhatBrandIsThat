
import argparse as ap
import cv2
import numpy as np
import os
from sklearn.externals import joblib
from scipy.cluster.vq import *
import sqlite3
from PIL import Image
import requests
from io import BytesIO
from sklearn import preprocessing
import math
from urllib.request import urlopen
import urllib
import time

# Get the training classes names and store them in a list

train_path = "dataset-retr/train/"


training_names = os.listdir(train_path)
print(training_names)


numWords = 1000

# Get all the path to the images and save them in a list
# image_paths and the corresponding label in image_paths
image_paths = []
for training_name in training_names:
    image_path = os.path.join(train_path, training_name)
    image_paths += [image_path]

# Create feature extraction and keypoint detector objects
# fea_det = cv2.FeatureDetector_create("SIFT")
# des_ext = cv2.DescriptorExtractor_create("SIFT")

# List where all the descriptors are stored
des_list = []
sift = cv2.xfeatures2d.SIFT_create()

for i, image_path in enumerate(image_paths):
    im = cv2.imread(image_path)
    print("Extract SIFT of %s image, %d of %d images" % (training_names[i], i, len(image_paths)))
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    kp, des = sift.detectAndCompute(gray, None)
    des_list.append((image_path, des))

# Stack all the descriptors vertically in a numpy array
# downsampling = 1
# descriptors = des_list[0][1][::downsampling,:]
# for image_path, descriptor in des_list[1:]:
#    descriptors = np.vstack((descriptors, descriptor[::downsampling,:]))

# Stack all the descriptors vertically in a numpy array
descriptors = des_list[0][1]
for image_path, descriptor in des_list[1:]:
    descriptors = np.vstack((descriptors, descriptor))

# Perform k-means clustering
print("Start k-means: %d words, %d key points" % (numWords, descriptors.shape[0]))
voc, variance = kmeans(descriptors, numWords, 1)

# Calculate the histogram of features
im_features = np.zeros((len(image_paths), numWords), "float32")
for i in range(len(image_paths)):
    words, distance = vq(des_list[i][1], voc)
    for w in words:
        im_features[i][w] += 1

# Perform Tf-Idf vectorization
nbr_occurences = np.sum((im_features > 0) * 1, axis=0)
idf = np.array(np.log((1.0 * len(image_paths) + 1) / (1.0 * nbr_occurences + 1)), 'float32')

# Perform L2 normalization
im_features = im_features * idf
im_features = preprocessing.normalize(im_features, norm='l2')

joblib.dump((im_features, image_paths, idf, numWords, voc), "bof_retr.pkl", compress=3)

#"bow_retrieval/dataset-retr/infos/matching.json"


print(image_paths)


                                                    # code utilise pour uploader des images sur noelshack et generer le fichier matching.json
API_URL = 'http://www.noelshack.com/api.php'
matching = open("dataset-retr/infos/matching.json","w")
matching.write('{ \r')
for i in range(0,len(training_names)):
    with open(image_paths[i], 'rb') as f:
        r = requests.post(API_URL, files={'fichier': f})
        url = r.text
        name = image_paths[i].split('/')[2]
        if "http://" not in url:                                                                                        # ici le chargement de l'image a echoue
            i=i-1                                                                                                       # nous essayons de revenir a l etape precedente
            continue                                                                                                    # nous reessayons
        if i < (len(image_paths)-1):                                                                                    # si nous n'avons pas atteint la derniere ligne
            matching.write('"'+name+'" : "' + url + '",\r')                                                             # nous ecrivons le correspondance  json forme { "nom" : "url" ,}
            time.sleep(1)                                                                                               # pause afin de ne pas se faire ejecter
        if i>=(len(image_paths)-1):
            matching.write('"' + name + '" : "' + url + '" \r')                                                         # ecriture du matching json forme { "nom" : "url" }
matching.write('}')
matching.close()



#API_URL = 'http://www.noelshack.com/api.php'
#file="dataset-retr/train/1.png"
#with open(file, 'rb') as f:
#    r = requests.post(API_URL, files={'fichier': f})

#print(r.text)