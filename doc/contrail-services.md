#1 Configuration Node

##1.1 Configuration API Server (active/active)
Mode: Active/Active  
Configuration: /etc/contrail/contrail-api.conf  
Log: Defined in configuration.  
Storage: Cassandra  
Port:  
  8082: REST API for read and write configuration  
  8084: introspec for debugging

### Cassandra
**Read:** Read configuration.  
**Write:** Write configuration.

### IF-MAP Server (local)
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


### Discovery
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


### Schema Transformer
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


### Service Monitor
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


### IF-MAP Server
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


### RabbitMQ
Configuration: /etc/rabbitmq/rabbitmq.config
Log: Defined in configuration. /var/log/rabbitmq
Port:
  5672

#### Configuration API Server
**Read:** Read configuration.
**Write:** Write configuration.


### Configuration Node Manager (server layer)
Monitor all config services in this node, send all stats to collector.
  - Collector


### User Configuration Flow
User Request
-> Original API Server
-> Local RabbitMQ
-> All API Servers
-> Local IF-MAP Server
-> Schema Transformer and Service Monitor


### Transformed Configuration Flow
Schema Transformer
-> Configuration API Server
-> Local RabbitMQ
-> All API Servers
-> Local IF-MAP Server
-> Control and DNS



## Analytics Node
# Analytics API Server
  - Cassandra
    - Read
    - Write

  - Redis
    - Read UVEs.

  - Collector


# Aalytics Node Manager
  - Collector


# Collector
  - Cassandra
    - Read
    - Write UVEs and logs.

  - Redis Server
    - Write UVEs.


# Qery Engine
  - Collector


# Redis Server
  - Collector
    - Read UVEs.

  - Analytics API Server
    - Write UVEs.


== Database ==
# Cassandra

Cluster size is the same as Replication factor.
Write and read levels are Quorum.

With 2n+1 cluster/replication-factor, reads are consistent.
Survive the loss of n nodes.
Really read from and write to n+1 nodes (quorum).
Each node holds 100% of data.



# Database Node Manager
  - Collector

# Zookeeper


== Control Node ==
# Control Node Manager
  - Collector


# Control
  - IF-MAP server
  - vRouger Agent
    XMPP messages
  - BGP peer
  - Collector

# DNS (Contrail)
  front-end of name resolving
  - IF-MAP Server
  - vRouger Agent
    XMPP messages
  - Collector

# named (host native)
  backend of name resolving


== Compute Node ==
# vRouter Agent
  - Collector

# vRouter Node Manager
  - Collector


