#!/usr/bin/env python

from urlparse import urlparse, parse_qs
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from lib import LicensePlate
from lib import Face

import BaseHTTPServer
import os.path
import sys
import json
import time
import prctl
import traceback
import logging
     
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

PID_FILE='/srv/www/pyms/stream.pid'
PORT_NUMBER=5081
                       
face = Face.Face()

class myHandler(BaseHTTPRequestHandler):
    
    def writeResponse(self,response):
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response))
        return 
    
    def do_HEAD(self):
        pass
    
    def do_GET(self):
        global face
        logging.info("Path = %s,"% (self.path));
        
        if 'cmd' in self.path: 
            try:
                query_components = parse_qs(urlparse(self.path).query)
                command = query_components["cmd"][0]
                image = query_components["image"][0]    
                
                if command == "lic":
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
                print "missing parameter ", e
                logging.info( "doGet failed")
                traceback.print_exc()
            except:
                logging.info( "Unknown issue doGet failed")
                traceback.print_exc()
                pass
          
    #def log_message(self, format, *args):
    #    return           
    
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    
    


if os.path.exists( PID_FILE ) and os.path.getsize( PID_FILE ) > 0:
    pid = int(open( PID_FILE,'rb').read().rstrip('\n'))
    count = int(os.popen('ps -ef | grep "%i" | grep -v "grep" | grep "%s" | wc -l ' % (pid, __file__)).read())
    if count > 0:
        print "Already Running as pid: %i" % pid
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
        print 'Unable to fork. Error: %d (%s)' % (error.errno, error.strerror)
        GPIO.cleanup()
        sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            print 'PID: %d' %pid
            os._exit(0)
        print 'pid 2', pid
    except OSError, error:
        print 'Unable to fork. Error: %d (%s)' % (error.errno, error.strerror)
        GPIO.cleanup()
        sys.exit(1)

    pf = open(PID_FILE,'wb')
    pf.write('%i\n' % os.getpid())
    pf.close()
    
    
    
    try:
        server = ThreadedHTTPServer(('', PORT_NUMBER), myHandler)
        #sys.stderr = open("/var/log/stream.log", "w")
        #print 'Starting httpserver on port ' , PORT_NUMBER
        prctl.set_name("pyms")
        time.sleep(1)
        server.serve_forever()
    
    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()




