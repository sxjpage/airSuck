"""
config.py by ThreeSixes (https://github.com/ThreeSixes)

This project is licensed under GPLv3. See COPYING for dtails.

This is the configuation file for the airSuck daemons and global client options for queues, except stateNode.js.

This file is part of the airSuck project (https://github.com/ThreeSixes/airSUck).
"""
# The Redis services can be on a single server or multiple servers. The queues are broken out like this for flexibility.

# Connector Redis queue settings - used by multliple scripts.
connRel = {host: "<insert hostname here>", port: 6379, reliableQ: "airSuckConnRel"};
connPub = {host: "<insert hostname here>", port: 6379, PubSubQ: "airSuckConnPub"};

# State engine Redis queue settings - used by multiple scripts.
stateRel = {host: "<insert hostname here>", port: 6379, reliableQ: "airSuckStateRel"};
statePub = {host: "<insert hostname here>", port: 6379, PubSubQ: "airSuckStatePub"};


# These databases can be stored on the same MongoDB server. The config is broken out for flexibility.

# SSR State engine settings
ssrStateEngine = {expireTime: 300, cprExpireSec: 20};

# mongoDump settings
connMongoDB = {host: "<insert hostname here>", port: 1, dbName: "airSuck", coll: "airSSR"};
connMongo = {checkDelay: 0.1};

# stateMongoDump settings
stateMongoDB = {host: "<insert hostname here>", port: 1, dbName: "airSuck", coll: "airState"};
stateMongo = {checkDelay: 0.1};