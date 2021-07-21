#!/usr/bin/env python

from botocore.exceptions import ClientError

import collections
import boto3
import cv2
import numpy
import os
import logging
import pickle
     
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


TRAIN_DATA_FOLDER='/srv/www/pyms/train_data/'
IMAGE_FOLDER='/srv/www/pyms/s3_images/'

s3 = boto3.resource('s3')
bucket = s3.Bucket("data.ibeyonde")


class TrainDataCache:
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        except KeyError:
            return -1

    def set(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value
        
         
    def loadTrainData(self, user_name):
        recognizer = self.get(user_name)
        if recognizer == -1:
            s3_key = "train_data/%s.pickle" % user_name
            file_name = TRAIN_DATA_FOLDER + user_name + ".pickle"  
            logging.info("Loading s3 key %s, file_name %s " %(s3_key, file_name))          
            #check from s3
            try:
                bucket.download_file(s3_key, file_name)
                with open(file_name,'rb') as rfp: 
                    recognizer = pickle.load(rfp)
            except ClientError as e:
                print "S3 file missing, Error on bucket download",e
                return None
        return recognizer;
          
    def saveTrainData(self, user_name, faces, ids):
        s3_key = "train_data/%s.pickle" % user_name
        file_name = TRAIN_DATA_FOLDER + user_name + ".pickle" 
        recognizer = self.loadTrainData(user_name)
        logging.info("Saving s3 key %s, file_name %s, ids %s " %(s3_key, file_name, ids))
        if recognizer is None:
            recognizer = {"faces": faces, "ids": ids}
        else:
            logging.debug("this is recog")
            logging.debug(recognizer)
            recognizer["faces"].extend(faces)
            recognizer["ids"].extend(ids)    
        
        f = open(file_name, "wb")
        f.write(pickle.dumps(recognizer))
        f.close()
        bucket.upload_file(file_name, s3_key)
        self.set(user_name, recognizer)
        logging.info("data saved returning true")
        return True
        
    
    