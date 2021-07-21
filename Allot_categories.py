#imagenet entry in database
#sublabels entry in database
from Utility import Database_connect
import logging
logging.basicConfig(filename= "allot_categories.log",level=logging.DEBUG ,format='[%(levelname)s] (%(threadName)-9s) %(message)s',)
cursor = Database_connect.dbs.cursor()
cursor.execute('select ID from SUBLABELS order by ID desc LIMIT 1')
row = cursor.fetchone()
MAX = row[0]

def find(label):
    
    global cursor
    cursor.execute("select SUBLABEL from LABELS where LABEL = %s ",(label))
    present = cursor.fetchone()
    return present[0]-1
            
            
def allot_categories():
    
    global MAX    
    global cursor
    MainDict = {}
    scoreDict = {}
    
    cursor.execute('select * from analytics where presence = 1 order by time')
    
    allrows = cursor.fetchall()
    
    logging.debug(allrows)
    
    for uuid,label,conf,count,time,presence in allrows:
        logging.debug("trying for uuid {}".format(uuid))
        try:
                      
            if(MainDict[uuid][0]!=3):
                
                
                logging.debug("count {} for {} for uuid {}".format(MainDict[uuid][0],time,uuid))
                
                MainDict[uuid][0] = MainDict[uuid][0] + 1  
                cat = find(label)
                logging.debug("label {}".format(cat)) 
                try:
                    logging.debug("saving score for {cat}") 
                    scoreDict[uuid][cat] = scoreDict[uuid][cat] + 1
                except KeyError:
                    scoreDict[uuid] = [0 for i in range(MAX)]
                    scoreDict[uuid][cat] = scoreDict[uuid][cat] + 1
            else:
                
                if MainDict[uuid][1] != time:
                    logging.debug("change in time for {}".format(uuid)) 
                    MainDict[uuid][1] = time
                    MainDict[uuid][0] = 1
                    cat = find(label) 
                    try:
                        scoreDict[uuid][cat] = scoreDict[uuid][cat] + 1
                    except KeyError:
                        scoreDict[uuid] = [0 for i in range(MAX)]
                        scoreDict[uuid][cat] = scoreDict[uuid][cat] + 1

                    
                
        except KeyError:
            
            logging.debug("intialisng MainDict for {}".format(uuid))
            MainDict[uuid] = [1,time]
            cat = find(label) 
            
            try:
                scoreDict[uuid][cat] = scoreDict[uuid][cat] + 1        
            except KeyError:
                
                logging.debug("intialisng scoreDict for {}".format(uuid))
                scoreDict[uuid] = [0 for i in range(MAX)] 
                scoreDict[uuid][cat] = scoreDict[uuid][cat] + 1

    logging.debug("the scores with keys are {}".format(scoreDict))
    cursor.execute("select uuid from camera_categories")
    uuids = cursor.fetchall()  
    new_uuids = []
    for uuid in uuids:
        new_uuids.append(uuid[0])         
    for key in scoreDict:
        
        cat = scoreDict[key].index(max(scoreDict[key])) + 1
        if (uuids is not None):
        
            if (key in new_uuids):
                cursor.execute("Update camera_categories set catgories = %s where uuid = %s",(cat,key))
            else:
                cursor.execute("INSERT INTO camera_categories values(%s,%s) ",(key,cat))    
                
                
        else:                
            cursor.execute("INSERT INTO camera_categories values(%s,%s) ",(key,cat))
        logging.debug("inserting to database")
        Database_connect.dbs.commit()
        
        
        
allot_categories()        
    
    




#mysql connection
#find top 3 categories based on time which are present for a uuid
#find the category for a label with weight conf * count
#calculate the category with best weights and assign it to uuid

 