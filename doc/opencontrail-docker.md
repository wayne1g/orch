# Docker with OpenContrail
## 1 Overview
OpenContrail is the infrastructure of building and managing overlay virtual networks. It's capable of connecting Docker contrainers across multiple service nodes into one or separate virtual networks, and connecting virtual networks based on defined policies.

![Docker containers with OpenContrail](opencontrail-docker-figure-1.png)

### 1.1 Connect Containers
VRouter, the forwarding engine of OpenContrail, is located in host kernel. A pare of veth interfaces (one end in kernel and another end in container) is created to connect vRouter and container.

### 1.2 Group Containers
Virtual networks can be created by OpenContrail to separate containers into different groups, and isolate traffic between different groups of containers.

### 1.3 Network Policy
By default, when virtual networks are created, they are all isolated from each other. Network policy needs to be created and attached to virtual networks to allow certain traffic between specific virtual networks.

Protocol, port and virtual network can be configured in the network policy to specify what traffic is allowed between which virtual networks.

### 1.4 Flow Statistics
OpenContrail is capable of collecting flow statistics and providing REST API interface for users to query. This makes it possible for users to create a feedback loop. By monitoring the traffic, users can check policy enforcement, change container deployment based on traffic load, etc.

### 1.5 Pysical/External Access
Floating IP is supported by OpenContrail to enable external access for containers. Gateway is required to support this feature.


## 2 Example
This example is based on OpenContrail 1.06 and Ubuntu 12.04.3.

### 2.1 Installation

#### 2.1.1 OpenContrail
[OpenContrail Installation](opencontrail-install.md)

#### 2.1.2 Docker

```
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
$ echo "deb https://get.docker.io/ubuntu docker main" | sudo tee -a /etc/apt/sources.list.d/docker.list
$ sudo apt-get update
$ sudo apt-get install lxc-docker
```

Download Ubuntu image and check if it works.
```
$ sudo docker run -i -t ubuntu /bin/bash
```

#### 2.1.3 Utility of Netns
```
$ git clone https://github.com/pedro-r-marques/opencontrail-netns.git
```
This utility does all configurations to connect vRouter and container.

#### 2.1.4 Utlity of Config
```
$ git clone https://github.com/tonyliu0592/orch.git
```
This utility does OpenContrail configurations. Update `config` with correct settings.

### 2.2 Connect Container to Virtual Network

#### Create Virtual Networks
Create two virtual networks, "red" and "green", in tenant "admin". Assume tenant "admin" is already created.
```
$ cd orch
$ ./config add ipam ipam-default
$ ./config add network red --ipam ipam-default --subnet 192.168.10.0/24
$ ./config add network green --ipam ipam-default --subnet 192.168.20.0/24
```

#### Create Containers
Create two containers. Type CTRL-p and CTRL-q to exit container and keep it running.
```
$ sudo docker run -i -t ubuntu /bin/bash
$ sudo docker run -i -t ubuntu /bin/bash
```

#### Connect Container to Virtual Network
Find out the container ID.
```
$ sudo docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
dccf1ec5a438        ubuntu:latest       "bash"              38 minutes ago       Up 38 minutes                           naughty_mcclintock
0996f6040d5d        ubuntu:latest       "bash"              38 minutes ago       Up 38 minutes                           sleepy_brown
```

Connect one container to each virtual network.
```
$ cd ../opencontrail-netns/opencontrail_netns
$ python docker.py -s <API server> -n red --project default-domain:admin --start dccf1ec5a438
$ python docker.py -s <API server> -n green --project default-domain:admin --start 0996f6040d5d
```

Now, two containers are connected to two virtual networks respectively. Policy needs to be created and attached to two virtual networks to allow traffic flow between each other.

#### Policy
Create a pass-all policy and attach to two virtual networks.
```
$ cd ../../orch
$ ./config add policy policy-default
$ ./config add network red --policy policy-default
$ ./config add network green --policy policy-default
```

Attach to container and test connection.
```
$ sudo docker attach dccf1ec5a438
root@dccf1ec5a438:/# ip addr show veth0
34: veth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 02:1a:74:99:fe:5f brd ff:ff:ff:ff:ff:ff
    inet 192.168.10.253/24 brd 192.168.10.255 scope global veth0
    inet6 fe80::1a:74ff:fe99:fe5f/64 scope link 
       valid_lft forever preferred_lft forever

root@dccf1ec5a438:/# ping 192.168.20.253
PING 192.168.20.253 (192.168.20.253) 56(84) bytes of data.
64 bytes from 192.168.20.253: icmp_seq=1 ttl=64 time=0.774 ms
64 bytes from 192.168.20.253: icmp_seq=2 ttl=64 time=0.066 ms

```



