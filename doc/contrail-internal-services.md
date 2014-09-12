#1 Configuration Node

##1.1 Configuration API Server (active/active)
Mode: Active/Active  
Configuration: /etc/contrail/contrail-api.conf  
Log: Defined in configuration.  
Storage: Cassandra  
Port:  
  8082: REST API for read and write configuration  
  8084: introspec for debugging

#### Cassandra
**Read:** Read configuration.  
**Write:** Write configuration.

#### IF-MAP Server (local)
**Read:** None  
**Write:** Publish configuration. This is driven by the configuration received from RabbitMQ.

#### RabbitMQ (default is local, configurable)
**Read:** Receive configuration sent from the API server who got user request originally.  
**Write:** The API server getting user request writes configuration to RabbitMQ for all API servers including itself. Then each API server will publish the configuration to IF-MAP server after receiving from RabbitMQ.

#### Collector
**Read:** None  
**Write:** Send positive (updates) and negtive (error, failures) logs, and running stats.

#### Discovery
**Read:** Get info of other services, like collector.  
**Write:** Register itself and IF-MAP server. Send heatbeat. Send request for other services.


##1.2 Discovery
Mode: Active/Active  
Configuration: /etc/contrail/contrail-discovery.conf  
Log: Defined in configuration.  
Storage: Zookeeper  
Port:  
  5998: REST API for register and request services

#### Other Services
**Read:** Recive registration (with VIP in HA case), service request and heartbeat.  
**Write:** Send requested service info.

#### Collector
**Read:** None  
**Write:** Send positive (updates) and negtive (error, failures) logs, and running stats.


##1.3 Schema Transformer
Mode: Active/Passive  
Configuration: /etc/contrail/contrail-schema.conf  
Log: Defined in configuration.  
Storage: Zookeeper  
Port:  
  8087: introspec for debugging

#### IF-MAP Server
**Read:** Receive configuration published by configuration API server.  
**Write:** None

#### Configuration API Server
**Read:** Read configuration.  
**Write:** Write configuration.

#### Zookeeper
**Read:** None  
**Write:** Register, first register, first being active. A callback is invoked if it is active. All other instances of schema transformer are passive and stuck at callback. Once the active one is down, one of the passive will be waked up by callback.

#### Collector
**Read:** None  
**Write:** Send positive (updates) and negtive (error, failures) logs, and running stats.


##1.4 Service Monitor
Mode: Active/Passive  
Configuration: /etc/contrail/svc-monitor.conf  
Log: Defined in configuration.  
Storage: Zookeeper  
Port:  
  8088: introspec for debugging

#### IF-MAP Server
**Read:** Receive configuration published by configuration API server.  
**Write:** None

#### Configuration API Server
**Read:** Read configuration.  
**Write:** Write configuration.

#### Zookeeper
**Read:** None  
**Write:** Register, first register, first being active. A callback is invoked if it is active. All other instances of schema transformer are passive and stuck at callback. Once the active one is down, one of the passive will be waked up by callback.

#### Collector
**Read:** None  
**Write:** Send positive (updates) and negtive (error, failures) logs, and running stats.


##1.5 IF-MAP Server
Configuration: /etc/ifmap-server/  
Log: Defined in configuration. /var/log/contrail/ifmap-server*.log  
Storage: Memory  
Port:  
  8443

#### Configuration API Server
**Read:** Read configuration published by API server, and store in memory (not persistent).  
**Write:** None

#### Schema Transformer
**Read:** None  
**Write:** Send published configuration.

#### Service Monitor
**Read:** None  
**Write:** Send published configuration.

#### Control (BGP)
**Read:** None  
**Write:** Send published configuration.

#### DNS
**Read:** None  
**Write:** Send published configuration.


##1.6 RabbitMQ
Configuration: /etc/rabbitmq/rabbitmq.config  
Log: Defined in configuration. /var/log/rabbitmq  
Port:  
  5672

#### Configuration API Server
**Read:** Read configuration.  
**Write:** Write configuration.


##1.7 Configuration Node Manager (server layer)
Monitor all config services in this node, send all stats to collector.

#### Collector
**Read:** None  
**Write:** Send positive (updates) and negtive (error, failures) logs, and running stats.


##1.8 User Configuration Flow
User Request  
-> Original API Server  
-> Local RabbitMQ  
-> All API Servers  
-> Local IF-MAP Server  
-> Schema Transformer and Service Monitor


##1.9 Transformed Configuration Flow
Schema Transformer  
-> Configuration API Server  
-> Local RabbitMQ  
-> All API Servers  
-> Local IF-MAP Server  
-> Control and DNS


#2 Analytics Node

##2.1 Analytics API Server

#### Cassandra
    - Read
    - Write

  - Redis
    - Read UVEs.

  - Collector


##2.2 Collector

#### Generators
**Read:** Receive UVEs and logs from all gnerators (services).  
**Write:** None

#### Redis Server
**Read:** None  
**Write:** Write UVEs into Redis server (caching).

#### Cassandra
**Read:** None
**Write:** Write all collected info.


##2.3 Qery Engine
  - Collector


##2.4 Redis Server
  - Collector
    - Read UVEs.

  - Analytics API Server
    - Write UVEs.

##2.5 Aalytics Node Manager
  - Collector



#3 Database

##3.1 Cassandra

Cluster size is the same as Replication factor.
Write and read levels are Quorum.

With 2n+1 cluster/replication-factor, reads are consistent.
Survive the loss of n nodes.
Really read from and write to n+1 nodes (quorum).
Each node holds 100% of data.



##3.2 Database Node Manager

#### Collector
**Read:** None  
**Write:** Send logs and running stats.


##3.3 Zookeeper


#4 Control Node

##4.1 Control

#### Discovery
**Read:** Receive info of requested services.  
**Write:** Request service info, eg. IF-MAP server.

#### IF-MAP Server
**Read:** Receive configurations published by configuration API server.  
**Write:** Subscribe to receive configurations.

#### vRouger Agent
**Read:** Receive XMPP messages.  
**Write:** Send XMPP messages.

#### BGP Peers
**Read:** Receive BGP.  
**Write:** Send BGP.

#### Collector
**Read:** None
**Write:** Send logs and running stats.


##4.2 DNS (Contrail)
This is the front-end of name resolving. Host native named is the back-end.

#### Discovery
**Read:** Receive info of requested services.  
**Write:** Request service info, eg. IF-MAP server.

#### IF-MAP Server
**Read:** Receive configurations published by configuration API server.  
**Write:** Subscribe to receive configurations.

#### vRouger Agent
**Read:** Receive XMPP messages.  
**Write:** Send XMPP messages.

#### Collector
**Read:** None
**Write:** Send logs and running stats.


##4.3 Control Node Manager

#### Collector
**Read:** None  
**Write:** Send logs and running stats.


#5 Compute Node

##5.1 vRouter Agent

#### Discovery
**Read:** Receive info of requested services.  
**Write:** Request service info, eg. control server.

#### Collector
**Read:** None  
**Write:** Send logs and running stats.


##5.2 vRouter
In kernel.

##5.3 vRouter Node Manager

#### Collector
**Read:** None  
**Write:** Send logs and running stats.


