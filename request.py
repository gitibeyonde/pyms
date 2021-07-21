from urllib2 import urlopen
import logging
from threading import Timer
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def requesting():
    logging.info("requesting function timer called")
    r = urlopen('https://bingo.ibeyonde.com:5081/?cmd=store&image=""')
    logging.info("request called")
    t = Timer(3.0,requesting())
    t.start()
    logging.info("loop started")

t = Timer(3.0,requesting)
t.start()    
logging.info("timer created")