#!/usr/bin/python

############
# Imports. #
############

import redis
import time
import json
import threading
from pprint import pprint

#################
# Configuration #
#################

# Which queue do we subscribe to?
targetSub = "airStateFeed"
targetHost = 'brick'

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
            locStr = ""
            
            if 'lat' in stateWrapped:
                # If we have ID data for the flight put it in.
                if 'idInfo' in stateWrapped:
                    locStr = stateWrapped['idInfo'] + " "
                
                # If we know the aircraft's squawk code add it, too.
                if 'aSquawk' in stateWrapped:
                    locStr = locStr + "(" + stateWrapped['aSquawk'] + ") " 
                
                # Add ICAO AA address.
                locStr = locStr + "[" + stateWrapped['addr'] + "]: "
                
                # Add coordinates.
                locStr = locStr + str(stateWrapped['lat']) + ", " + str(stateWrapped['lon'])
                
                # If we know the altitude put it in, too.
                if 'alt' in stateWrapped:
                    locStr = locStr + " @ " + str(stateWrapped['alt']) + "ft"
                
                # If we know the vertical rate put it in as well.
                if 'vertRate' in stateWrapped:
                    signExtra = ""
                    
                    # Determine sign.
                    if stateWrapped['vertRate'] > 0:
                        signExtra = "+"
                    
                    # Add sign and unit to string.
                    locStr = locStr + " (" + signExtra + str(stateWrapped['vertRate']) + "ft/min)"
                
                # Put in the heading if we know it.
                if 'heading' in stateWrapped:
                    locStr = locStr + " - " + str(stateWrapped['heading']) + " deg"
                
                # Add aircraft category if we know it.
                if 'category' in stateWrapped:
                    locStr = locStr + "; cat " + stateWrapped['category']
                
                if 'fs' in stateWrapped:
                    locStr = locStr + " [" + str(stateWrapped['fs']) + "]"
                
                # Add vertical status if we know it (air/ground)
                if 'vertStat' in stateWrapped:
                    locStr = locStr + " (" + stateWrapped['vertStat'] + ")"
                
                print(locStr)
        
        
    def run(self):
        for work in self.pubsub.listen():
            self.worker(work)

if __name__ == "__main__":
    print("airSuck state queue viewer starting...")
    r = redis.Redis(targetHost)
    client = SubListener(r, [targetSub])
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
        print("Unhandled exception:")
        pprint(e)