# System Design

### Must Learn System Design Concepts
+  Consistent Hashing
+  CAP Theorem
+  Load Balancing
+  Caching
+  Data Partitioning
+  Indexes
+  Proxies
+  Queues
+  Replication
+  SQL vs. NoSQL.
+ Latency vs Throughput
---------------

### Important System Design Algorithms To Read Before Interview

+ Trie algorithm  
+ Reverse index  
+ Frugal Streaming  
+ Geo-hashing  
+ Leaky bucket, Token bucket and its variation  
+ Bloom Filters  
+ Operational transformation  
+ Quadtree / Rtree  
+ Loose Counting  
+ XMPP / Web Sockets uses  
+ HTTP Long polling  
+ Consistent Hashing

**Credit** - [Soumyajit Bhattacharyay](https://www.linkedin.com/in/soumyajit-bhattacharyay-4a897611a/)
**[Post](https://www.linkedin.com/posts/soumyajit-bhattacharyay-4a897611a_scalability-systemdesign-hld-activity-6726135149836152832-luGH/)**

---------

### System Design Terminologies
Scalability, Availability, Efficiency, Reliability, Serviceability, Manageability, Extensible, Client-Server, Protocol, Proxy, Gateway, DNS, Latency, Throughput, Read Heavy, Write Heavy, 

------------
### Best System Design Interview Format Or Flow
+ Clarifying Questions
+ Functional Requirements
+ Non Functional Requirements
+ Capacity/Storage Estimation
+ Drawing Constraints
+ Design Database Schema
+ Design APIs
+ Basic Architecture And Data Flow
+ Components or Functionality Implementation
+ Trade offs And Corner Cases
 

## Article Links
+ [ The complete guide to crack the System Design interview](https://towardsdatascience.com/the-complete-guide-to-the-system-design-interview-ba118f48bdfc)
+ [ Scalable Web Architecture and Distributed Systems](http://www.aosabook.org/en/distsys.html)
+ [ System Design Interview Questions – Concepts You Should Know](https://www.freecodecamp.org/news/systems-design-for-interviews/)
+ [25 Software Design Interview Questions to Crack Any Programming and Technical Interviews](https://medium.com/javarevisited/25-software-design-interview-questions-to-crack-any-programming-and-technical-interviews-4b8237942db0)
+ [ Top 10 System Design Interview Questions and Answers](https://www.geeksforgeeks.org/top-10-system-design-interview-questions-and-answers/)
+ [Getting Started With System Design](https://www.geeksforgeeks.org/getting-started-with-system-design/?ref=rp)
+ [How To Crack System Design Round in Interviews](https://www.geeksforgeeks.org/how-to-crack-system-design-round-in-interviews/?ref=rp)
+ https://www.geeksforgeeks.org/what-is-web-socket-and-how-it-is-different-from-the-http/
+ https://www.tutorialspoint.com/websockets/index.htm
+ https://javascript.info/long-polling
+ https://www.pubnub.com/blog/http-long-polling/
+ https://hackernoon.com/understand-service-discovery-in-microservice-c323e78f47fd
+ https://dzone.com/articles/service-discovery-in-a-microservices-architecture


## Best Engineering Blogs or Platform To Follow For System Design
+ [HighScalability](http://highscalability.com/)
+ [ The Architecture of Open Source Applications](http://www.aosabook.org/en/)
+ [A Distributed Systems Reading List](http://dancres.github.io/Pages/)
+ [Interviewbit System Design](https://www.interviewbit.com/courses/system-design/)
+  [Linkedin Engineering](https://engineering.linkedin.com/)
+ 

## Best Documentations For System Design
+ [System design primer in Github](https://github.com/donnemartin/system-design-primer)
+  [AWS Documentation](https://docs.aws.amazon.com/)
+ [System Design Cheatsheet](https://gist.github.com/vasanthk/485d1c25737e8e72759f)
+ [ System Design Prepration](https://github.com/shashank88/system_design)
+ [Grokking System Design Interview Github](https://github.com/lei-hsia/grokking-system-design)

## Best Youtube Channels And Playlists For System Design
+ [Gaurav Sen](https://www.youtube.com/channel/UCRPMAqdtSgd0Ipeef7iFsKw)
+ [Gaurav Sen System Design Playlist](https://www.youtube.com/playlist?list=PLMCXHnjXnTnvo6alSjVkgxV-VH6EPyvoX)
+ [Tech Dummies](https://www.youtube.com/channel/UCn1XnDWhsLS5URXTi5wtFTA)
+ [Tech Dummies's System Design Playlist](https://www.youtube.com/playlist?list=PLkQkbY7JNJuBoTemzQfjym0sqbOHt5fnV)
+ [sudoCODE](https://www.youtube.com/channel/UCMrRRZxUAXRzjai0SSoFgdw/featured)
+ [sudoCODE System Design's Basics Playlist](https://www.youtube.com/playlist?list=PLTCrU9sGyburBw9wNOHebv9SjlE4Elv5a)
+ [System Design Interview](https://www.youtube.com/channel/UC9vLsnF6QPYuH51njmIooCQ)
+ [Think Software](https://www.youtube.com/c/ThinkSoftware/featured)
+ [Think Software's System Design Playlist](https://www.youtube.com/playlist?list=PLK8IOvtbwVsuYW8KovGg9o6dlhspym8O_)
+ [Amazon Web Services](https://www.youtube.com/c/amazonwebservices/featured)
+ [Tech Takshila](https://www.youtube.com/channel/UC_n-A84J0UcU5uq4sEh2CnQ/featured)
+ [codeKarle](https://www.youtube.com/channel/UCZEfiXy7PmtVTezYUvc4zZw)
+ [Success in Tech](https://www.youtube.com/channel/UC-vYrOAmtrx9sBzJAf3x_xw)
+ [Basics Of System Design Playlist](https://www.youtube.com/playlist?list=PLt4nG7RVVk1g_LutiJ8_LvE914rIE5z4u)
+ [The Stupid CS Guy](https://www.youtube.com/channel/UCUm1OB1gDV0Tl0Mjx5I01-A)
+ [Tushar Roy's System Design Playlist](https://www.youtube.com/playlist?list=PLrmLmBdmIlps7GJJWW9I7N0P0rB0C3eY2)
+ [Tech Primers](https://www.youtube.com/c/TechPrimers/featured)
+ [Distributed Systems Course](https://www.youtube.com/user/cbcolohan)
+ [Udit Agarwal](https://www.youtube.com/user/UDIT19911)


**Note** Content is under continuous development phase. it contains some terminologies and concepts which really helps when you are thinking about systems.

-------------------

## Content 

+ Long Polling
+ Websockets
+ Service Discovery
+ Heartbeats
+ SQL vs NoSQL

-----------------------------------------------------------

### Long Polling 
Web app developers can implement a technique called HTTP long polling, where the client polls the server requesting new information. The server holds the request open until new data is available. Once available, the server responds and sends the new information. When the client receives the new information, it immediately sends another request, and the operation is repeated. This effectively emulates a server push feature.
![Long Polling](https://user-images.githubusercontent.com/29687692/85210917-c0703480-b361-11ea-81f3-0c7acd59f45c.png)
The flow:

1.  A request is sent to the server.
2.  The server doesn’t close the connection until it has a message to send.
3.  When a message appears – the server responds to the request with it.
4.  The browser makes a new request immediately.

------------------------
### WebSockets
Web sockets are defined as a two-way communication between the servers and the clients, which mean both the parties, communicate and exchange data at the same time. This protocol defines a full duplex communication from the ground up. Web sockets take a step forward in bringing desktop rich functionalities to the web browsers. It represents an evolution, which was awaited for a long time in client/server web technology.

![WebSocket](https://media.geeksforgeeks.org/wp-content/uploads/20191203183648/WebSocket-Connection.png)
### WebSocket Uses
+ **Real-time web application**
+ **Gaming application**
+ **Chat application**
--------------------
### Gateway
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

### Service Discovery
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

---------------------

### SQL vs NoSQL

#### When to pick a SQL database?

If you are writing a stock trading, banking, or a Finance-based app or you need to store a lot of relationships, for instance, when writing a social networking app like Facebook, then you should pick a relational database. Here’s why:

**Transactions & Data Consistency**

If you are writing software that has anything to do with money or numbers, that makes transactions, ACID, data consistency super important to you. Relational DBs shine when it comes to transactions & data consistency. They comply with the ACID rule, have been around for ages & are battle-tested.

**Storing Relationships**

If your data has a lot of relationships like which friends of yours live in a particular city? Which of your friend already ate at the restaurant you plan to visit today? etc. There is nothing better than a relational database for storing this kind of data.

Relational databases are built to store relationships. They have been tried & tested & are used by big guns in the industry like Facebook as the main user-facing database.

Popular relational databases:

-   [MySQL](https://www.educative.io/blog/mysql-tutorial)
-   Microsoft SQL Server
-   PostgreSQL
-   MariaDB

#### When to pick a NoSQL database

Here are a few reasons why you want to pick a NoSQL database:

**Handling A Large Number Of Read Write Operations**

Look towards NoSQL databases when you need to scale fast. For example, when there are a large number of read-write operations on your website and when dealing with a large amount of data, NoSQL databases fit best in these scenarios. Since they have the ability to add nodes on the fly, they can handle more concurrent traffic and large amounts of data with minimal latency.

**Running data analytics** NoSQL databases also fit best for data analytics use cases, where we have to deal with an influx of massive amounts of data.

Popular NoSQL databases:

-   MongoDB
-   Redis
-   Cassandra
-   HBASE

-----------------

**Note** Suggestions are Welcome
