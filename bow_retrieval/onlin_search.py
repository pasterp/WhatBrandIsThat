import cv2
import os
from sklearn.externals import joblib
from scipy.cluster.vq import *
import sqlite3
import json
from sklearn import preprocessing
import numpy as np


def return_img_list(img_path,id_cree):

    # Get query image path
    image_path = img_path

    # Load the classifier, class names, scaler, number of clusters and vocabulary
    im_features, image_paths, idf, numWords, voc = joblib.load("bow_retrieval/bof_retr.pkl")

    # Create feature extraction and keypoint detector objects
    # List where all the descriptors are stored
    des_list = []
    sift = cv2.xfeatures2d.SIFT_create()



    im = cv2.imread(image_path)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    kp, des = sift.detectAndCompute(im, None)

    des_list.append((image_path, des))

    # Stack all the descriptors vertically in a numpy array
    descriptors = des_list[0][1]

    #
    test_features = np.zeros((1, numWords), "float64")
    words, distance = vq(descriptors, voc)
    for w in words:
        test_features[0][w] += 1

    # Perform Tf-Idf vectorization and L2 normalization
    test_features = test_features * idf
    test_features = preprocessing.normalize(test_features, norm='l2')

    score = np.dot(test_features, im_features.T)

    rank_ID = np.argsort(-score)                                                                                        # les images sont classees par scores


    idlist=[]
    for i, ID in enumerate(rank_ID[0][0:16]):
        idlist.append(str(image_paths[ID]).replace('dataset-retr/train/',''))                                           # contient le nom de l'imgage sans extension

    images_triees=idlist
    scores_tries=sorted(score[0],reverse=True)


    list_to_write_indb={}
    for i in range(0,len(idlist)):
        list_to_write_indb[idlist[i]]=scores_tries[i]

    with open('bow_retrieval/dataset-retr/infos/matching.json') as f :                                                  # nous chargeons le fichier de correspondance json pour avoir un mini wikipedia
        data=json.load(f)

    conn = sqlite3.connect("db.sqlite3")                                                                                # nous nous connections a la BdD
    cursor = conn.cursor()
    for i in range(0,len(list_to_write_indb)):                                                                          # nous stockons tous les resultats lies a la recherche du client
        cursor.execute('INSERT INTO url_responses(request_id,image_url,score) VALUES (?,?,?)', (id_cree,data[images_triees[i]],str(scores_tries[i])[:5],))
    conn.commit()
    conn.close()
    os.remove(image_path)                                                                                               # nous supprimons l image pour economiser de la place





