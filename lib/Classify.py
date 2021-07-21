import cv2
import numpy as np
import logging
from skimage import io
import time
from multiprocessing import Lock
mutex = Lock()
class StartClassify:
    def __init__(self,net,image,s_client):
        
        self.url = s_client.generate_presigned_url(ClientMethod='get_object',Params={'Bucket':'data.ibeyonde','Key':image})
        self.image = io.imread(self.url)
        
        self.preds = None 
        self.blob = cv2.dnn.blobFromImage(self.image, 1, (224, 224), (104, 117, 123))
        self.net = net
        self.idxs = None
        self.label = ''


    def compute(self,classes):
        
        global mutex
        mutex.acquire()
        logging.info("lock acquired by thread")
        self.net.setInput(self.blob)
        start = time.time()
        self.preds = self.net.forward()
        end = time.time()
        logging.info("[INFO] classification took {:.5} seconds".format(end - start))
        
        self.idxs = np.argsort(self.preds[0])[::-1][:1]
        
        for (i, idx) in enumerate(self.idxs):
        
            self.label = self.label + ("{} ".format(classes[idx]))
            
        
        mutex.release()
        logging.info("lock relased by thread")
            
        return {'label':self.label}
