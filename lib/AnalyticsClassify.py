import cv2
import numpy as np
import logging
from skimage import io
import time
from multiprocessing import Lock
mutex = Lock()

class AClassify:
    def __init__(self,uuid,net,image,s_client):
        logging.debug("intialisation is requested")
        self.url = s_client.generate_presigned_url(ClientMethod='get_object',Params={'Bucket':'data.ibeyonde','Key':image})
        self.image = io.imread(self.url)
        self.preds = None 
        self.blob = cv2.dnn.blobFromImage(self.image, 1, (224, 224), (104, 117, 123))
        self.net = net
        self.idxs = None
        self.new_label = []
        self.uuid = uuid

    def compute(self,classes):
        logging.debug("Aclassify computation is requested")
        global mutex
        mutex.acquire()
        logging.info("lock acquired by thread")
        self.net.setInput(self.blob)
        start = time.time()
        self.preds = self.net.forward()
        end = time.time()
        logging.info("[INFO] analytics took {:.5} seconds".format(end - start))
        
        self.idxs = np.argsort(self.preds[0])[::-1][:5]
        
        logging.info(self.idxs)
        for idx in self.idxs:
            label = classes[idx]
            if label.endswith('\r'):    
                label = label[:-1]
            self.new_label.append({label:self.preds[0][idx]})
                                       
        mutex.release()
        logging.info("lock relased by thread")
        return self.uuid,self.new_label

