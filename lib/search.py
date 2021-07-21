'''
Created on Mar 21, 2018

@author: siddharth
'''
import colordescriptor
import searcher
import argparse
import cv2
import glob
from skimage import io 
from skimage.transform import resize
import boto3
import time
from datetime import date, timedelta
import datetime
import logging
import traceback
import sys
import os

class search:
	fromdate = None
	todate = None
	s3= None
	#current_time = None
	bucket_name = None
	bucket = None
	index = None
	cd = None
	output = None
	fromdate = None
	todate = None
	objss = None
	d1 = None
	d2 = None
	delta = None
	cameras  = None
	fromtime = None
	totime = None
	def __init__(self,fromtime,totime,fromdate,todate,cameras):
		logging.info(" constructor search intialised")
		#change as per username
		logging.debug(fromdate)
		self.fromdate = fromdate
		self.todate = todate
		self.fromtime = int(fromtime)
		self.totime = int(totime)	
		self.s3 = boto3.resource('s3')
		#self.current_time = str(int(time.time()))
		self.bucket_name = "data.ibeyonde"
		self.bucket = self.s3.Bucket("data.ibeyonde")
		self.cd = colordescriptor.ColorDescriptor((8,12,3)) 
		self.time = time.time()
		self.fromdate = self.fromdate.split('-')
		self.todate = self.todate.split('-')		
		self.objss = list()
		self.cameras = cameras
	
		self.d1 = date(int(self.fromdate[0]), int(self.fromdate[1]), int(self.fromdate[2]))  # start date
		self.d2 = date(int(self.todate[0]),int(self.todate[1]) , int(self.todate[2]))  # end date

		self.index = "/srv/www/iapp.ibeyonde.com/public_html/tmp/"+str(int(self.time))+".csv"                                
		self.output = open(self.index,'w')

		self.delta = self.d2 - self.d1         # timedelta
		
		if (self.totime==00):
   			self.totime = 24 
		
		
		for uuid in cameras:
			
			for i in range(self.delta.days + 1):
				
			    self.current_date = self.d1 + timedelta(i)
			    
			    self.current_date=datetime.datetime.strptime(str(self.current_date), '%Y-%m-%d').strftime('%Y/%m/%d')
			    for new_time in range(self.fromtime,self.totime):
			    	self.objss.append(uuid+'/'+self.current_date+'/'+str(new_time).zfill(2))
		
		logging.info(self.objss)    		
		self.s_client  = boto3.client('s3')
		logging.info("starting to create a datset")
		for objs in self.objss:
			nobjs = self.bucket.objects.filter(Prefix=objs)

			
			for obj in nobjs:
				
				
				key = obj.key
				logging.debug(key)
				url = self.s_client.generate_presigned_url(ClientMethod='get_object',Params={'Bucket':'data.ibeyonde','Key':key})
				try:
					image = io.imread(url)
				except:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
					logging.critical('error in searching image'.join('!! ' + line for line in lines))

					#logging.warning("Connection error: reset by the peer");
					
				imageID = key
			   	#print imageID
			   	features = self.cd.describe(image)
			   	features = [str(f) for f in features]
			   	self.output.write("%s,%s\n"%(imageID, ",".join(features)))
		logging.info("dataset Created")	   	
		self.output.close()    

	def now_search(self,url,x1,y1,height,width,hheight,hwidth):	
		
		# intialise the color descriptor with 
		
		# read the image
		self.url = self.s_client.generate_presigned_url(ClientMethod='get_object',Params={'Bucket':'data.ibeyonde','Key':url})
		self.query = io.imread(self.url)
		logging.info("Image read from the url")
		logging.debug(self.query)
	
		self.query = cv2.resize(self.query,(hwidth,hheight))
		self.query = self.query[y1:y1+height,x1:x1+width]
		cv2.imwrite('/srv/www/pyms/crop.jpg',self.query)
		logging.info("image cropped successfully")
		logging.debug(self.query)
		# extract the features of the image
		self.queryFeature = self.cd.describe(self.query)
		#intialise the search
		logging.info("cropped image features extracted")
		logging.debug(self.queryFeature) 
		self.result_obj = searcher.Searcher(self.cameras,self.index)
		#search the datafile for matched 
		self.result = self.result_obj.search(self.queryFeature,20)
		logging.info("resulting images extracted")
		logging.debug (self.result)
		os.remove(self.index)
		return self.result

		