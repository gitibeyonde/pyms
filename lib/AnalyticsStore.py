import MySQLdb
import logging
import sqlite3
import datetime
import time
class AnalyticsStore:
    
    def __init__(self):
        
        self.db = sqlite3.connect(':memory:',check_same_thread=False)
        self.c = self.db.cursor()
        self.time = datetime.datetime.now().hour
        self.flag = 0
        self.c.execute('''
        CREATE table analytics 
        (
        uuid VARCHAR (100) NOT NULL,
        label VARCHAR (100) NOT NULL,
        conf REAL NOT NULL,
        count INT NOT NULL
        )''')
        self.db.commit()
        for row in self.c.execute('select * from analytics'):
           logging.info(row) 
        
                        
    def store(self,uuid,labelvalues):
        
        
        #currentHour = datetime.datetime.now().minute
        currentHour = datetime.datetime.now().hour
        logging.info(currentHour)
        logging.info(self.time)
        if (self.time==currentHour):
            
            for labelvalue in labelvalues:    
                for label,conf in labelvalue.items():
                    self.c.execute("select * from analytics where label = ? and uuid = ?",(label,uuid))
                    present  = self.c.fetchone()
                    if present!=None:
                        previous_count = present[3]
                        previous_conf  = present[2]
                        logging.debug("count"+str(previous_count))
                    
                        new_count = previous_count + 1 
                        conf = ((previous_conf*previous_count)+conf)/new_count
                        self.c.execute("UPDATE analytics SET conf = ? , count = ? where label = ? and uuid = ?",(conf,new_count,label,uuid))
                        self.db.commit()
                    else:
                         
                        self.c.execute("INSERT INTO analytics (uuid,label,conf,count) values (?,?,?,?)",(str(uuid),str(label),float(conf),1))                
                        self.db.commit()
        
        else:
            print self.flag
            if(self.flag == 0):          
                self.flag =1
                self.dbStore()
                self.time = currentHour
                self.flag=0
                self.store(uuid, labelvalues)
            
            else:
                while(self.flag==1):
                    logging.info("going to sleep")
                    time.sleep(1)
                logging.info("waking and calling again")        
                self.store(uuid,labelvalues)
                
                    
        return  
        
                        
    def dbStore(self):
        
        logging.info("dbStore called")
        dbs = MySQLdb.connect("mysql.ibeyonde.com","admin","1b6y0nd6","ibe" )
        mainS = dbs.cursor()
        mainS.execute("UPDATE analytics SET presence = 0 where time =%s",(self.time))
        dbs.commit()
        for uuid,label,conf,count in self.c.execute('select * from analytics'):
            
            mainS.execute("select * from analytics where label = %s and uuid = %s and time=%s",(label,uuid,self.time))
            present  = mainS.fetchone()
            logging.info(present)
            
            if(present!=None):
                logging.debug(present)
                previous_count = present[3]
                previous_conf = present[2]
                new_count = previous_count+count
                conf = ((previous_conf*previous_count)+(conf*count))/new_count
                logging.debug(conf)
                logging.debug(new_count)
                mainS.execute("UPDATE analytics SET conf = %s, count = %s ,presence = %s where label = %s and uuid = %s and time=%s",(conf,new_count,1,label,uuid,self.time))
             
            else:  
                
                mainS.execute("INSERT INTO analytics (uuid,label,conf,count,time,presence) values (%s,%s,%s,%s,%s,%s)",(str(uuid),str(label),str(conf),str(count),str(self.time),1))                
            dbs.commit()
        self.c.execute("DELETE FROM analytics")
        self.db.commit()   
        logging.info("stored in db")    
        
            
        
    
    
    def display(self):
        
       for row in self.c.execute('select * from analytics'):
           logging.info(row) 
                     
            
        
        