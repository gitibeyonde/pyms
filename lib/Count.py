import cv2
import numpy as np
from skimage import io
from skimage.transform import resize
import boto3
import logging

def non_max_suppression_slow(boxes, overlapThresh):
    # if there are no boxes, return an empty list
        if len(boxes) == 0:
            return []
    
        # initialize the list of picked indexes
        pick = []
    
        # grab the coordinates of the bounding boxes
        x1 = boxes[:,0]
        y1 = boxes[:,1]
        x2 = boxes[:,2]
        y2 = boxes[:,3]
    
        # compute the area of the bounding boxes and sort the bounding
        # boxes by the bottom-right y-coordinate of the bounding box
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)
    
        # keep looping while some indexes still remain in the indexes
        # list
        while len(idxs) > 0:
            # grab the last index in the indexes list, add the index
            # value to the list of picked indexes, then initialize
            # the suppression list (i.e. indexes that will be deleted)
            # using the last index
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            suppress = [last]
    
            # loop over all indexes in the indexes list
            for pos in xrange(0, last):
                # grab the current index
                j = idxs[pos]
    
                # find the largest (x, y) coordinates for the start of
                # the bounding box and the smallest (x, y) coordinates
                # for the end of the bounding box
                xx1 = max(x1[i], x1[j])
                yy1 = max(y1[i], y1[j])
                xx2 = min(x2[i], x2[j])
                yy2 = min(y2[i], y2[j])
    
                # compute the width and height of the bounding box
                w = max(0, xx2 - xx1 + 1)
                h = max(0, yy2 - yy1 + 1)
    
                # compute the ratio of overlap between the computed
                # bounding box and the bounding box in the area list
                overlap = float(w * h) / area[j]
    
                # if there is sufficient overlap, suppress the
                # current bounding box
                if overlap > overlapThresh:
                    suppress.append(pos)
    
            # delete all indexes from the index list that are in the
            # suppression list
            idxs = np.delete(idxs, suppress)
    
        # return only the bounding boxes that were picked
        return boxes[pick]


class Count:
    def __init__(self,image):
        self.image = image
        self.s_client  = boto3.client('s3')
        self.url = self.s_client.generate_presigned_url(ClientMethod='get_object',Params={'Bucket':'data.ibeyonde','Key':image})
        self.head_cascade = cv2.CascadeClassifier('/srv/www/pyms/config/heads_cascade.xml')
        self.shoulder_cascade = cv2.CascadeClassifier('/srv/www/pyms/config/HS.xml')
        self.profile_face = cv2.CascadeClassifier('/srv/www/pyms/config/haarcascade_profileface.xml')
        self.boundingBoxes = list()
        self.count = None
   
   
    
    def count_people(self):
        self.image = io.imread(self.url)    
        self.image = cv2.resize(self.image,(self.image.shape[0] / 2, self.image.shape[1] / 4))
        logging.debug(self.image)
        self.gray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY)
        logging.debug(self.gray)
        self.heads = self.head_cascade.detectMultiScale(self.gray,1.1,5)
        self.shoulder = self.shoulder_cascade.detectMultiScale(self.gray,1.1,3)
        self.profile_face = self.profile_face.detectMultiScale(self.gray,1.1,4)
        for (x,y,w,h) in self.heads:
            
            self.boundingBoxes.append((x,y,x+w,y+h))
            
        
        for (x,y,w,h) in self.shoulder:
            
            self.boundingBoxes.append((x,y,x+w,y+h))
            
        for (x,y,w,h) in self.profile_face:
            
            self.boundingBoxes.append((x,y,x+w,y+h))    
            
        
        self.boundingBoxes = np.array(self.boundingBoxes)
        logging.info(self.boundingBoxes)
        self.pick = non_max_suppression_slow(self.boundingBoxes, 0.1)
        self.count = len(self.pick)
        
        return {'no_of_people':self.count}
        
        
        
        
        
        
