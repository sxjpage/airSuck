#!/usr/bin/python

############
# Imports. #
############

import redis
import time
import json
import threading
import binascii
from pprint import pprint
from ssrParse import ssrParse

#################
# Configuration #
#################

# Which queue do we subscribe to?
targetSub = "ssrFeed"
targetHost = "127.0.0.1"

# Set up the SSR parser
ssrEngine = ssrParse()
# Turn on decoding of names
#ssrEngine.setReturnNames(True)

##############################
# Classes for handling data. #
##############################

class SubListener(threading.Thread):
    """
    Listen to the SSR channel for new data formatted as a hex string
    """
    def __init__(self, r, channels):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
    
    def worker(self, work):
        # Do work on the data returned from the subscriber.
        ssrJson = str(work['data'])
        
        # Get wrapped SSR data.
        ssrWrapped = json.loads(ssrJson)
        
        # Make sure we got good data from json.loads
        if (type(ssrWrapped) == dict):
            
            # Get the hex data as a string
            strMsg = ssrWrapped['data']
            
            # Convert the ASCII hex data to a binary string.
            binData = binascii.unhexlify(strMsg)
            
            # Parse the SSR data as a dict.
            parsed = ssrEngine.ssrParse(binData)
            
            # Add the processed fields to our existing info.
            ssrWrapped.update(parsed)
            
            # Now sort the data by key alphabetically for easy viewing.
            sorted(ssrWrapped)
            
            # Flatten the data so it's more easily searched.
            jsonData = json.dumps(ssrWrapped)
            
            # Dump the data
            print(jsonData)
        
        
    def run(self):
        for work in self.pubsub.listen():
            self.worker(work)

if __name__ == "__main__":
    print("ADSB subscription queue data parsing test engine starting...")
    
    # Set up Redis queues.
    r = redis.Redis(host=targetHost)
    
    # Start up our ADS-B parser
    client = SubListener(r, [targetSub])
    
    # .. and go.
    client.start()
