//  dump1090Client.js by ThreeSixes (https://github.com/ThreeSixes)
//
//  This project is licensed under GPLv3. See COPYING for dtails.
//
//  This file is part of the airSuck project (https://github.com/ThreeSixes/airSUck).

// Settings
var cfg = require('./config.js');
var config = cfg.getConfig();

// Set up our needed libraries.
var net = require('net');
var d1090 = new net.Socket();
var dConn = new net.Socket();

// Vars
var dConnConnected = false;

// Log event.
function log(eventText) {
    // Just do a console.log().
    console.log(new Date().toISOString().replace(/T/, ' ') + ' - ' + eventText);
}

// Process message arrays.
function handleMessage(message) {
    
    // Loop through messages we got at the same time.
    for(i = 0; i < message.length; ++i) {
        
        // If we have non-empty data...
        if (message[i] != "") {
            // Handle our data frame.
            data = {'dts': new Date().toISOString().replace('T', ' ').replace('Z', ''), 'src': config.client1090.srcName, 'dataOrigin': 'dump1090', 'data': message[i]}
            
            // Convert the data object to a JSON string.
            data = JSON.stringify(data)
            
            // Log the frmae for debugging.
            //log("Load frame: " + data);
            
            // If we're connected to the connector server...
            if (dConnConnected) {
                // Send the data to our connector instance. 
                dConn.write(data + "\n");
                //log("Send frame: " + data);
            }
        }
    }
}

// Connect to our source dump1090 instance to get the "binary" frame data.
function connect2Dump1090() {
    // Connect up, log connection success.
    d1090.connect(config.client1090.dump1090Port, config.client1090.dump1090Host, function() {
        log('Connected to dump1090 instance at ' + config.client1090.dump1090Host + ':' + config.client1090.dump1090Port);
    });
}

// Connect to our destination dump1090 connector instance to send JSON data.
function connect2Connector() {
    // Connect up, log connection success.
    dConn.connect(config.client1090.connPort, config.client1090.connHost, function() {
        log('Connected to dump1090 connector at ' + config.client1090.connHost + ':' + config.client1090.connPort);
        dConnConnected = true;
    });
}

// When we get data...
d1090.on('error', function(err) {
    // Puke error message out.
    log("Dump1090 socket " + err);
    
    // Destroy the connection since we don't want it anymore...
    d1090.destroy();
    
    // Find a way to wait for n amount of time.
    
    // Attempt reconnect.
    connect2Dump1090();
});

// When we get data...
d1090.on('data', function(data) {
    // Object -> String
    data = data.toString();
    
    // String -> Array
    data = data.split("\n");
    
    // Do something useful with the message.
    handleMessage(data)
});

// When the connection is closed...
d1090.on('close', function() {
    log('Dump1090 connection to ' + config.client1090.dump1090Host + ':' + config.client1090.dump1090Port + ' closed');
    
    // Attempt reconnect.
    connect2Dump1090();
});

// When we get data...
dConn.on('error', function(err) {
    // Puke error message out.
    log("Dump1090 connector socket " + err);
    
    dConn.destroy();
    
    dConnConnected = false;
    
    // Find a way to wait for n amount of time.
    
    // Attempt reconnect.
    connect2Connector();
});

// When we get data from the connector...
dConn.on('data', function(data) {
    // Do nothing.
});

// When the connection is closed...
dConn.on('close', function() {
    log('Dump1090 connector connection to ' + config.client1090.connHost + ':' + config.client1090.connPort + ' closed');
    dConnConnected = false;
    
    // Attempt reconnect
    connect2Connector();
});


// Make the initial attempt to connect, assuming we're enabled.
if (config.client1090.enabled) {
    log("Starting dump1090 client...")
    connect2Connector();
    connect2Dump1090();
} else {
    log("Dump1090 client not enabled in configuration, but executed.")
}