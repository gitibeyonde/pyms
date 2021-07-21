
from botocore.exceptions import ClientError
from contextlib import closing

import boto3
import cv2
import TrainDataCache
import MySQLdb
import numpy
import sys
import os
import traceback
import logging
import face_recognition     
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


TRAIN_DATA_FOLDER='/srv/www/pyms/train_data/'
IMAGE_FOLDER='/srv/www/pyms/s3_images/'
DB_HOST='mysql.ibeyonde.com'
DB_USER='admin'
DB_PASS='1b6y0nd6'
DB='ibe'
tolerance = 0.5
s3 = boto3.resource('s3')
bucket = s3.Bucket("data.ibeyonde")

class Face:
    data_cache=None
            
    def __init__(self):
        self.data_cache = TrainDataCache.TrainDataCache(10)
   
    
    def insertTrainData(self, cur, id, user, person):
        sql = "insert into face_recog(train_data,user_name,person_name) values (%s,%s,%s)"
        cur.execute(sql,(id, user, person))
        logging.info("Initially Inserting %s, %s, %s, %s " %( id, user, person ,sql))
        return id


    def getTrainDataId(self, user, person):
        file_name = TRAIN_DATA_FOLDER + user + ".pickle" 
        logging.info( "file-name %s" % file_name)
        conn =  MySQLdb.connect(DB_HOST,DB_USER,DB_PASS,DB) 
        cur = conn.cursor()
        try:
            if os.path.isfile(file_name):
                sql = 'select train_data from face_recog where user_name=%s AND person_name=%s'
                logging.info("Check id for user %s person %s query %s" %( user, person, sql))
                row_count = cur.execute(sql,(user,person))
                if(row_count>0):
                    results = cur.fetchone()
                    id = int(results[0])
                    return id
                else:
                    sql = 'select train_data from face_recog where user_name=%s order by train_data desc limit 1;'
                    logging.info("Check id for user %s query %s" %( user, sql))
                    row_count = cur.execute(sql, user)
                    if(row_count>0):
                        result = cur.fetchone()[0]
                        id = int(result) + 1
                        return self.insertTrainData(cur, id, user, person)
                    else:
                        return self.insertTrainData(cur, 1, user, person)
            else:
                return self.insertTrainData(cur, 1, user, person)
        except:
            logging.info( "getTrainDataId failed")
            traceback.print_exc()
        finally:
            cur.close()
            conn.commit()
            
        return -1

        
    def train(self, user, image, person):
        global bucket
        response = dict()
        
        try:
            faces = []
            ids = []
            temp_image = IMAGE_FOLDER + user + ".jpg" 
            bucket.download_file(image, temp_image)
            my_image = cv2.imread(temp_image)
            rgb = cv2.cvtColor(my_image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb,model='cnn')
            encodings = face_recognition.face_encodings(rgb, boxes)
            id = self.getTrainDataId(user, person)

    # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                faces.append(encoding)
                ids.append(id)
                
            if id == -1 :
                response['name'] = "failed"
                response['conf'] = -1
                return response
            logging.info("Traning for %s %s %s "%(user, faces, ids));
            status = self.data_cache.saveTrainData(user, faces, ids)
            response['name'] = status
            response['conf'] = -1
        except:
            print("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
        #remove temp_image file
        return response
    
    def predict(self, user, image):
        global bucket
        global tolerance
        response = dict()
        
        conn =  MySQLdb.connect(DB_HOST,DB_USER,DB_PASS,DB) 
        try:
            
            cur = conn.cursor()
            temp_image = IMAGE_FOLDER + user + ".jpg" 
            bucket.download_file(image, temp_image)
            my_image = cv2.imread(temp_image)
            rgb = cv2.cvtColor(my_image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb,model="cnn")                                                                             
            encodings = face_recognition.face_encodings(rgb, boxes)
            recognizer = self.data_cache.loadTrainData(user)
            for encoding in encodings:
                matches = face_recognition.compare_faces(recognizer["faces"],encoding,tolerance=tolerance)
                
            id = -1
        # check to see if we have found a match
            
            if True in matches:
    
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
    
                
                for i in matchedIdxs:
                    id = recognizer["ids"][i]
                    counts[id] = counts.get(id, 0) + 1
    
                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                
                id = max(counts, key=counts.get)
            
            # update the list of names
            

            if id!=-1:
                logging.info("Predicting face for %s %s " % (user,id))
                row_count = cur.execute("select person_name from face_recog where user_name =%s AND  train_data =%s",(user,id))
                if (row_count > 0) :
                    person_name = cur.fetchone()[0]
                    response['name'] = person_name
                    response['conf'] = tolerance
            else :
                response['name'] = "unknown"
                response['conf'] = "0"
                
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.critical(''.join('!! ' + line for line in lines))
        finally:
            cur.close()
        
        return response

            