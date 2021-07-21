#features extraction
'''
Created on Mar 20, 2018

@author: siddharth
'''
import numpy as np
import cv2
from numpy import uint, dtype

class ColorDescriptor:
    def __init__(self,bins):
        #intialising the no of bins fot the histogram
        self.bins = bins
        
            
    def describe(self,image):
        # Convert image to HSV color model
        image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        # Intialising the features list
        features = []
        # computing the width and height of image
        w,h = image.shape[0:2]
        # computing the centre of image
        cX,cY = (int(w*0.5),int(h*0.5))
        # computing the four regions of the image(top left, top right,bottom right, bottom left)
        segments = [(0,cX,0,cY),(cX,w,0,cY),(cX,w,cY,h),(0,cX,cY,h)]
        # compute the length of major axis and minor axis
        axX,axY = (int(w*0.75),int(h*0.75))
        # create an mask with image shape
        ellipMask = np.zeros(image.shape[:2],dtype = "uint8" )
        # draw a white ellipse inside the mask
        cv2.ellipse(ellipMask,(cX,cY),(axX,axY),0,0,360,255,-1)
        # loop for masking for rectangle corners
        for startX,endX,startY,endY in segments:
            
            rectMask = np.zeros(image.shape[:2],dtype = "uint8" )
            cv2.rectangle(rectMask,(startX,startY),(endX,endY),255,-1)
            #subtract elliptical mask from rectangle
            rectMask = cv2.subtract(rectMask,ellipMask)
            
            
            #calculate the histogram using the image and mask
            hist = self.histogram(image,rectMask)
            #add the feature to the list
            
            features.extend(hist)
        #add the elliptical region features to list 
        hist = self.histogram(image,ellipMask)
        #add the elliptical region features to list
        features.extend(hist)
        return features
        
    def histogram(self,image,mask):
        
        hist = cv2.calcHist([image],[0,1,2],mask,self.bins,[0,180, 0, 256, 0, 256])
        hist = cv2.normalize(hist,hist).flatten()
        
        return hist    
