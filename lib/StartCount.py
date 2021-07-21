import cv2
import time
import numpy as np
import logging
from skimage import io
from multiprocessing import Lock
mutex = Lock()
class StartCount:
    
    
    def __init__(self,net,image,s_client):
        
        self.unique = time.time()
        self.url = s_client.generate_presigned_url(ClientMethod='get_object',Params={'Bucket':'data.ibeyonde','Key':image})
        self.image = io.imread(self.url)
        self.detections = None 
        (self.h, self.w) = self.image.shape[:2]
        self.blob = cv2.dnn.blobFromImage(cv2.resize(self.image, (227, 227)), 0.007843, (227, 227), 127.5)
        self.net = net
        self.count = 0 
        self.idx = None
        self.i = 0
        logging.info("object cretaed with id"+str(self.unique))
        
    def compute(self):
        global mutex
        mutex.acquire()
        logging.info("lock acquired by thread")
        logging.info("computation with id "+str(self.unique))
        self.net.setInput(self.blob)
        start = time.time()
        self.detections = self.net.forward()
        end = time.time()
        logging.info("[INFO] classification took {:.5} seconds".format(end - start))
        self.count = 0 
        self.confidence = None
        
        
        for self.i in np.arange(0,self.detections.shape[2]):
            
            self.confidence = self.detections[0,0,self.i,2]
            
            if self.confidence>0.2:
                
                
                self.idx = int(self.detections[0,0,self.i,1])
                
                if (self.idx ==15):
                    
                    self.count = self.count + 1
                    logging.debug(str(self.unique)+" id counting is "+str(self.count))
        
        logging.info("lock relased by thread")
        mutex.release()    
        return {'no_of_people':self.count}        
    
    
    
    
    
    
    
    
    
    
    
    
    