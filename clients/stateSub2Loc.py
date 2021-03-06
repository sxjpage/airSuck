#!/usr/bin/python

"""
stateSub2Loc by ThreeSixes (https://github.com/ThreeSixes)

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

#################
# Configuration #
#################


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
			locStr = "SSR -> "
			
			if stateWrapped['type'] == "airSSR":
				
				if 'lat' in stateWrapped:
					# If we have ID data for the flight put it in.
					if 'idInfo' in stateWrapped:
						locStr =  locStr + "%s " %stateWrapped['idInfo']
					
					# If we know the aircraft's squawk code add it, too.
					if 'aSquawk' in stateWrapped:
						locStr = locStr + "(%s) " %stateWrapped['aSquawk'] 
					
					# Add ICAO AA address.
					locStr = locStr + "[%s]: " %stateWrapped['addr']
					
					# Add coordinates.
					locStr = locStr + "%s, %s" %(stateWrapped['lat'], stateWrapped['lon'])
					
					# If we know the altitude put it in, too.
					if 'alt' in stateWrapped:
						locStr = locStr + " @ %s ft" %stateWrapped['alt']
					
					# If we know the vertical rate put it in as well.
					if 'vertRate' in stateWrapped:
						signExtra = ""
					
						# Determine sign.
						if stateWrapped['vertRate'] > 0:
					    		signExtra = "+"
					
						# Add sign and unit to string.
						locStr = locStr + " (%s%s ft/min)" %(signExtra, stateWrapped['vertRate'])
					
					if 'velo' in stateWrapped:
					
						if 'supersonic' in stateWrapped:
						    if stateWrapped['supersonic'] == True:
						        ssExtra = "**"
						    else:
						        ssExtra = ""
					
						locStr = locStr + ", %s%s kt (%s)" %(ssExtra, stateWrapped['velo'], stateWrapped['veloType'])
					
					# Put in the heading if we know it.
					if 'heading' in stateWrapped:
						locStr = locStr + ", %s deg" %stateWrapped['heading']
					
					# Add aircraft category if we know it.
					if 'category' in stateWrapped:
						locStr = locStr + ", cat %s" %stateWrapped['category']
					
					if 'fs' in stateWrapped:
						locStr = locStr + " [%s]" %stateWrapped['fs']
					
					# Add vertical status if we know it (air/ground)
					if 'vertStat' in stateWrapped:
						locStr = locStr + " (%s)" %stateWrapped['vertStat']
					
					print(locStr)
	
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
		# Die nicely.
		quit()
	except:
		tb = traceback.format_exc()
		print("Unhandled exception:\n%s" %tb)
