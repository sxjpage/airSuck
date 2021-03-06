#!/usr/bin/python

"""
subState2Console by ThreeSixes (https://github.com/ThreeSixes)

This project is licensed under GPLv3. See COPYING for dtails.

This file is part of the airSuck project (https://github.com/ThreeSixes/airSUck).
"""

############
# Imports. #
############

import sys
sys.path.append("..")

try:
	import config
except:
	raise IOError("No configuration present. Please copy config/config.py to the airSuck folder and edit it.")

import redis
import time
import json
import threading
import traceback
from pprint import pprint


##############################
# Classes for handling data. #
##############################

class SubListener(threading.Thread):
    """
    Listen to the ADSB channel for new data.
    """
    def __init__(self, r, channels):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
    
    def worker(self, work):
        #Do work on the data returned from the subscriber.
        stateJson = str(work['data'])
        stateWrapped = json.loads(stateJson)
        
        # Make sure we got good data from json.loads
        if (type(stateWrapped) == dict):
            print(str(stateWrapped))
    
    def run(self):
        for work in self.pubsub.listen():
            self.worker(work)

if __name__ == "__main__":
    print("airSuck state queue viewer starting...")
    r = redis.Redis(host=config.statePub['host'], port=config.statePub['port'])
    client = SubListener(r, [config.statePub['qName']])
    # We want the faote of our SubListener instance to be tied to the main thread process.
    client.daemon = True
    client.start()
    
    try:
        # Fix bug that doesn't allow Ctrl + C to kill the script
        while True: time.sleep(10)
    except KeyboardInterrupt:
        # Die incely.
        quit()
    except Exception as e:
        tb = traceback.format_exc()
        print("Unhandled exception:\n%s" %tb)
