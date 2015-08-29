var webPort = 8090;
var redisPort = 6379;
var redisHost = "brick";
var redisQueue = 'airStateFeed';

var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var redis = require('redis');
var client = redis.createClient(redisPort, redisHost);

var glbSocket = null

// Serve index.html
app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

// When we have a message in Redis send it to all connected clients. 
client.on("message", function (channel, message) {
  io.emit("message", message)
  //console.log("MSG: " + message)
});

// When have a new socket.io connection...
io.on('connection', function(socket){
  // Log a message to the console
  console.log("New client @ " + socket.request.connection.remoteAddress)
  
  // If they try to send us something give some generic error message.
  socket.on('message', function(msg){
    socket.emit("message", "{\"error\": \"Yeah, no.\"}");
  });
});

// Start the HTTP server up on our specified port.
http.listen(webPort, function(){
  console.log('airSuck-stateNode.js listening on *:' + webPort);
});

// Subscribe to the state queue.
client.subscribe(redisQueue);
