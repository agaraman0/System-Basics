# System Design

### Content 

+ Long Polling
+ Websockets
+ Service Discovery
+ Heartbeats
+ 

+ Article Links
-----------------------------------------------------------
## Long Polling 
Web app developers can implement a technique called HTTP long polling, where the client polls the server requesting new information. The server holds the request open until new data is available. Once available, the server responds and sends the new information. When the client receives the new information, it immediately sends another request, and the operation is repeated. This effectively emulates a server push feature.
![Long Polling](https://user-images.githubusercontent.com/29687692/85210917-c0703480-b361-11ea-81f3-0c7acd59f45c.png)

The flow:
1.  A request is sent to the server.
2.  The server doesn’t close the connection until it has a message to send.
3.  When a message appears – the server responds to the request with it.
4.  The browser makes a new request immediately.

------------------------

## WebSockets

Web sockets are defined as a two-way communication between the servers and the clients, which mean both the parties, communicate and exchange data at the same time. This protocol defines a full duplex communication from the ground up. Web sockets take a step forward in bringing desktop rich functionalities to the web browsers. It represents an evolution, which was awaited for a long time in client/server web technology.

![WebSocket](https://media.geeksforgeeks.org/wp-content/uploads/20191203183648/WebSocket-Connection.png)

### WebSocket Uses
+ **Real-time web application**
+ **Gaming application**
+ **Chat application**

--------------------

## Gateway

A **gateway** is a piece of [networking hardware](https://en.wikipedia.org/wiki/Networking_hardware "Networking hardware") used in [telecommunications](https://en.wikipedia.org/wiki/Telecommunication "Telecommunication") for telecommunications networks that allows data to flow from one discrete network to another. Gateways are distinct from [routers](https://en.wikipedia.org/wiki/Router_(computing) "Router (computing)") or [switches](https://en.wikipedia.org/wiki/Network_switch "Network switch") in that they communicate using more than one protocol to connect a bunch of networks and can operate at any of the seven layers of the [open systems interconnection](https://en.wikipedia.org/wiki/OSI_model "OSI model") model (OSI).

A gateway is a network node that connects two networks using different protocols together. While a bridge is used to join two similar types of networks, a gateway is used to join two dissimilar networks.

Gateways can take several forms and perform a variety of tasks:

-   **Web application firewall** - filters traffic to and from a web server and look at application-layer data
-   **Cloud gateway** - provides basic protocol translation and simple connectivity to allow the incompatible technologies to communicate transparently
-   **API, SOA or XML gateway** - manages traffic flowing into and out of a service, microservices-oriented architecture or an XML-based web service
-   **IoT gateway** - aggregates sensor data, translates between sensor protocols, processes sensor data before sending it onward and more
-   **Cloud storage gateway** - translates storage requests with various cloud storage service API calls
-   **Media gateway** - converts data from the format required for one type of network to the format required for another
-   **Amazon API Gateway** - allows a developer to connect non-AWS applications to AWS back-end resources
-   **VoIP trunk gateway** - facilitates the use of plain old telephone service (POTS) equipment, such as landline phones and fax machines, with a voice over IP (VoIP) network
-   **Email security gateway** - prevents the transmission of emails that break company policy or will transfer information with malicious intent

-------------------------

## Service Discovery

**Service discovery** is the automatic detection of devices and services offered by these devices on a [computer network](https://en.wikipedia.org/wiki/Computer_network "Computer network"). A **service discovery protocol** (**SDP**) is a [network protocol](https://en.wikipedia.org/wiki/Network_protocol "Network protocol") that helps accomplish service discovery. Service discovery aims to reduce the configuration efforts from users.

Service discovery requires a common language to allow software agents to make use of one another's services without the need for continuous user intervention.

Service discovery involves 3 parties: service provider, service consumer and service registry.

1.  service provider registers itself with service registry when it enters and deregister itself when it leaves the system.
2.  service consumer gets the location of a provider from registry, and then talks to the provider.
3.  service registry maintains the latest location of providers.

**complexities to handle:**

1.  **The service may not deregister itself when it’s gone**. Then the registry provides an invalid address to the consumer. To tackle this problem, service provider needs to send its **_heartbeat_** periodically (every 5 second maybe). If the provider hasn’t send any heartbeat for sometime, the registry will assume the death of provider, and deregister it.
2.  **Querying registry before calling provider every time?** It’s place too much load on registry and impose unnecessary performance impact. It’s better to keep a copy in consumer itself.
3.  **If kept in consumer, how to notify consumer about the changes in provider?** There are 2 ways to do it. 1) consumer use **_polling_** to get latest version. Since the locations usually don’t change so frequently, this still works. The drawback is the possible downtime between polling. 2) **_pubsub_** pattern. It provides more immediate update of locations, but it will hold up additional thread of consumer.
4.  **Sending back all data of a provider may not be necessary.** We can keep a **_global versioning_** of providers and consumer only needs to update its local copy when version got incremented.
5.  **Single point of failure**. If the service registry (e.g. the redis instance we are using here) is down, all consumer and provider will be affected. To alleviate this, we can use a **_distributed database_** as service registry, such as `zookeeper/etcd/consul` .













# Article Links
+ https://www.geeksforgeeks.org/what-is-web-socket-and-how-it-is-different-from-the-http/
+ https://www.tutorialspoint.com/websockets/index.htm
+ https://javascript.info/long-polling
+ https://www.pubnub.com/blog/http-long-polling/
+ https://hackernoon.com/understand-service-discovery-in-microservice-c323e78f47fd
+ https://dzone.com/articles/service-discovery-in-a-microservices-architecture
