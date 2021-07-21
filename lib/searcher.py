#to search the features in the db
import numpy as np
import csv
import json
import boto3
class Searcher:
    
    # intilaise the path of image
    def __init__(self,cameras,index):
        
        self.cameras = cameras
        self.index = index
    def chi2_distance(self,histA,histB  ,eps=1e-10):
        
        d = 0.5 * np.sum([((a-b)**2)/(a+b+eps) for (a,b) in zip(histA,histB)])
        return d
    # search the image for features    
    def search(self,queryFeatures,limit=50):
        
        #intilaise the result dictionary
        results={}
        features = list()    
        s_client  = boto3.client('s3')
        #open the csv feature file
        
            
        with open(self.index) as f:
            # read the image
            reader = csv.reader(f)
        
        #looping over different rows of features    
            for row in reader:
                
                features = [float(x) for x in row[1:]]
                d = self.chi2_distance(features,queryFeatures)
                results[row[0]] = d
                
        f.close()    
        # sort the results in increasing order       
        results = sorted([(v,k) for (k, v) in results.items()])
        new_results = {}
        count =0
        for (k, v) in results:
            if(count==limit):
                break
            url = s_client.generate_presigned_url(ClientMethod='get_object',Params={'Bucket':'data.ibeyonde','Key':v})    
            new_results[count] = url

            count = count + 1    

        # return the result
        return new_results
        
        