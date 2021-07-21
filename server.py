#!/usr/bin/env python
from Utils import __ROOT__
import logging
from warnings import _getcategory
import uuid as oo
logging.basicConfig(filename= __ROOT__+"/logs/server.log",level=logging.DEBUG ,format='[%(levelname)s] (%(threadName)-9s) %(message)s',)
from urlparse import urlparse, parse_qs
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from lib import LicensePlate
from lib import Face
from lib import LabelAndCategory
from lib import aws
from lib import search
from lib import Count
from lib import New_count
from lib import StartCount
from lib import GetCategory
from lib import Classify
from lib import AnalyticsClassify
from lib import AnalyticsStore
import BaseHTTPServer
import os.path
import sys
import json
import time
import prctl
import traceback
import ssl



PID_FILE=__ROOT__+'/stream.pid'
PORT_NUMBER=5081                       
face = Face.Face()
CountNet = New_count.CountClassifier()
analytics = AnalyticsStore.AnalyticsStore()



class myHandler(BaseHTTPRequestHandler):
    
    def writeanotherResponse(self,id,response):
        self.send_response(200,'success')
        self.send_header('Content-Type','application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('apns-id', id)
        self.end_headers()
        self.wfile.write(json.dumps(response))
        return 
    
    def writeResponse(self,response):
        self.send_response(200,'success')
        self.send_header('Content-Type','application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response))
        return 
    
    def do_HEAD(self):
        pass
    
    def log_message(self, format, *args):
        return
       
    
    def do_GET(self):
        global face
        global CountNet
        logging.info("Path = %s,"% (self.path));
            
        if 'cmd' in self.path: 
            try:
                query_components = parse_qs(urlparse(self.path).query)
                command = query_components["cmd"][0]
                image = query_components["image"][0]    
                
                if command == "test":
                    self.writeResponse({1:'success'})
                
                elif command=="Aclassify":
                    
                    uuid = query_components["uuid"][0]
                    logging.info("Analytics is requested")
                    obj = AnalyticsClassify.AClassify(uuid,CountNet.classify,image,CountNet.s_client)
                    logging.debug("analyticsClassify is intialised")    
                    uuid,response=obj.compute(CountNet.classes)
                    logging.info(uuid)
                    logging.info(response)
                    analytics.store(uuid,response)
                    response=LabelAndCategory.LabelCategory(uuid,response)
                    self.writeResponse(response)
                    
                elif command =="count":
                    logging.info("count value is requested")
                    obj_count = Count.Count(image)
                    response = obj_count.count_people()
                    self.writeResponse(response)
                    
                elif command =="new_count":
                    logging.info("new count value is requested")
                    obj = StartCount.StartCount(CountNet.net,image,CountNet.s_client)    
                    response=obj.compute()
                    logging.info(response)
                    self.writeResponse(response)
                    
                elif command =="classify":
                    logging.info("classification is requested")
                    obj = Classify.StartClassify(CountNet.classify,image,CountNet.s_client)    
                    response=obj.compute(CountNet.classes)
                    logging.info(response)
                    self.writeResponse(response)    
                    
                
                elif command == "search":

                    logging.info("template search is requested")
                    fromdate  = query_components["fromdate"][0]
                    todate = query_components["to_date"][0]
                    logging.debug(fromdate)
                    from_time = query_components["from_time"][0]
                    to_time = query_components["to_time"][0]
                    x1 = int(query_components["x1"][0])
                    y1 = int(query_components["y1"][0])
                    height = int(query_components["height"][0])
                    width = int(query_components["width"][0])
                    hheight = int(query_components["hheight"][0])
                    hwidth = int(query_components["hwidth"][0])
                    cameras = query_components['cameras'][0]
                    logging.debug(cameras)
                    cameras = cameras.split(",")
                    logging.debug(cameras)
                    logging.info("template search is intialising")
                                                                         
                    try:
                        se = search.search(fromtime = from_time,totime=to_time,cameras=cameras,fromdate=fromdate,todate=todate)
                    except:
                         
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                        logging.critical(''.join('!! ' + line for line in lines))

                    else:
                        logging.info("template intialise is completed")
                        logging.info("server going to image search")
                        try:    
                            image_responses=se.now_search(image,x1,y1,height,width,hheight,hwidth)
                        except:
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                            logging.critical('error in searching image'.join('!! ' + line for line in lines))
                        else:                            
                            logging.info("server gathered the responses")
                            
                            self.writeResponse(image_responses)
                                                        
            
                elif command == "lic":
                    response = {'lic':0}
                    Lit1,Lit2 = LicensePlate.detect(image)
                    
                    if Lit2 is None:
                        response['lic']=Lit1
                        response['lic1']=None
                    else:
                        response['lic']=Lit1
                        response['lic1']=Lit2
                    self.writeResponse(response)        
                
                elif command == "face":
                    
                    user = query_components["user"][0]
                    method = query_components["method"][0]
                    if (method == 'train'):
                        person =  query_components["person"][0]
                        train_response = face.train(user, image, person)
                        self.writeResponse(train_response)  
                    elif (method == 'predict'):
                        predict_response = face.predict(user, image)
                        self.writeResponse(predict_response)
                    else:
                        logging.info("wrong method %s" % method)
                            
                else:
                    logging.info("unrecognized command %s" % command)
                    self.writeResponse({'commands': "lic, face"})
                    
                    
            except KeyError, e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                logging.critical('error in server'.join('!! ' + line for line in lines))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                logging.critical('error in server'.join('!! ' + line for line in lines))
                pass    
                
          
    #def log_message(self, format, *args):
    #    return           
    
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    
    

if os.path.exists( PID_FILE ) and os.path.getsize( PID_FILE ) > 0:
    pid = int(open( PID_FILE,'rb').read().rstrip('\n'))
    count = int(os.popen('ps -ef | grep "%i" | grep -v "grep" | grep "%s" | wc -l ' % (pid, __file__)).read())
    if count > 0:
       logging.info( "Already Running as pid: %i" % pid)
       sys.exit(1)
# If we get here, we know that the app is not running so we can start a new one...


if __name__ == "__main__":
    try:
        pid = os.fork()
        if pid > 0:
            #print 'PID: %d' %pid
            os._exit(0)
        #print 'pid 1', pid
    except OSError, error:
        logging.info( 'Unable to fork. Error: %d (%s)' % (error.errno, error.strerror))
        GPIO.cleanup()
        sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            logging.info( 'PID: %d' %pid)
            os._exit(0)
        logging.info( 'pid 2 %d' %pid)
    except OSError, error:
        logging.critical( 'Unable to fork. Error: %d (%s)' % (error.errno, error.strerror))
        GPIO.cleanup()
        sys.exit(1)

    pf = open(PID_FILE,'wb')
    pf.write('%i\n' % os.getpid())
    pf.close()
    
    
    
    try:
        server = ThreadedHTTPServer(('', PORT_NUMBER), myHandler)
        #sys.stderr = open("/var/log/stream.log", "w")
        #print 'Starting httpserver on port ' , PORT_NUMBER
        server.socket = ssl.wrap_socket(server.socket, certfile=__ROOT__+'/keys/server.pem', server_side=True)
        prctl.set_name("pyms")
        time.sleep(1)
        logging.info("timer created")
        server.serve_forever()
    
    except KeyboardInterrupt:
        logging.info ('^C received, shutting down the web server')
        server.socket.close()




