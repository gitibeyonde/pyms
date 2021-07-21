
#import the packages
import numpy as np
import cv2
from Utils import __ROOT__
import logging
import boto3
#List of classes that can predicted by the model
class CountClassifier:
    
    def __init__(self):
        
        logging.info("[INFO] loading classify model...")
        self.classify = cv2.dnn.readNetFromCaffe(__ROOT__+'/classifiers/prototxt/classify.prototxt',__ROOT__+'/classifiers/model/classify.caffemodel')
        rows = open(__ROOT__+'/classifiers/labels/labels.txt').read().strip().split("\n")
        self.classes = [r[r.find(" ") + 1:].split(",")[0] for r in rows]

        logging.info("[INFO] loading count model...")
        self.net = cv2.dnn.readNetFromCaffe(__ROOT__+'/classifiers/prototxt/CountModel.prototxt.txt',__ROOT__+'/classifiers/model/CountModel.caffemodel')
        self.s_client  = boto3.client('s3')
        
        

