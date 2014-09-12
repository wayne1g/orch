# scp 10.84.5.112:/cs-shared/images/ubuntu-12.04.3.qcow2 ./
# glance image-create --name ubuntu-12.04.3 --disk-format qcow2 --container-format bare --min-ram 2048 --file /root/ubuntu.qcow2 --is-public True

## Tenant "admin", network "public" with public IP subnet, network "data" with internal IP subnet.

# nova boot --flavor m1.large --image ubuntu-12.04.3 --nic net-id=dbebd472-564f-432c-9610-be40ef446561 --nic net-id=643a7137-eb02-4c84-baa8-90f8eb6c5f72,v4-fixed-ip=10.8.1.10 docker-config
# nova boot --flavor m1.medium --image ubuntu-12.04.3 --nic net-id=dbebd472-564f-432c-9610-be40ef446561 --nic net-id=643a7137-eb02-4c84-baa8-90f8eb6c5f72,v4-fixed-ip=10.8.1.11 docker-compute

# config delete vm-interface docker-compute:public --security-group default
# config delete vm-interface docker-config:public --security-group default



# Host System
Ubuntu installation is based on ubuntu-12.04.3-server-amd64.iso.
Installation server option is OpenSSH server.
Kernel version is 3.8.0-29-generic #42~precise1-Ubuntu.

# Host Name
Host name with interface IP has to be properly set in /etc/hosts before start.


# Configuration Node

## Install Packages

$ echo "deb http://ppa.launchpad.net/opencontrail/ppa/ubuntu precise main" | sudo tee -a /etc/apt/sources.list.d/opencontrail.list
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 16BD83506839FE77
$ echo "deb http://debian.datastax.com/community stable main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
$ curl -L http://debian.datastax.com/debian/repo_key | sudo apt-key add -
$ sudo apt-get update

$ sudo apt-get install cassandra=1.2.18
$ sudo apt-get install zookeeperd
$ sudo apt-get install rabbitmq-server
$ sudo apt-get install ifmap-server
$ sudo apt-get install contrail-config

$ sudo apt-get install contrail-web-controller


## Cassandra
By default, Cassandra listens to 127.0.0.1:9160 only.

## Zookeeper

## RabbitMQ

## IP-MAP Server

$ echo "control:control" | sudo tee -a /etc/ifmap-server/basicauthusers.properties
$ sudo service ifmap-server restart

## Configuration API Server

$ curl http://127.0.0.1:8082/projects | python -mjson.tool

## Schema Transformer

## Service Monitor

## Discovery

$ curl http://127.0.0.1:5998/services
$ curl http://127.0.0.1:5998/clients


# Analytics Node

## Install Packages

$ wget http://mirrors.kernel.org/ubuntu/pool/universe/r/redis/redis-server_2.6.13-1_amd64.deb
$ sudo apt-get install libjemalloc1
$ sudo dpkg -i redis-server_2.6.13-1_amd64.deb

$ echo "deb http://ppa.launchpad.net/opencontrail/ppa/ubuntu precise main" | sudo tee -a /etc/apt/sources.list.d/opencontrail.list
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 16BD83506839FE77
$ sudo apt-get update

$ sudo apt-get install contrail-analytics

## Redis

/etc/init/redis-uve.conf
--------------------------------------------------------------------
# redis-server UVE
#

description     "redis-server UVE"

start on runlevel [2345]
stop on runlevel [!2345]

chdir /var/run
respawn

script
  COMMAND="/usr/bin/redis-server"
  CONF="/etc/contrail/redis-uve.conf"

  # Allow override of command/conf and opts by /etc/default/daemon-name
  if [ -f /etc/default/$UPSTART_JOB ]; then
    . /etc/default/$UPSTART_JOB
  fi

  if ! [ -r "$CONF" ] ; then
    echo "Could not read ${CONF}: exiting"
    exit 0
  fi

  exec start-stop-daemon --start \
        --pidfile /var/run/${UPSTART_JOB}.pid \
        --exec $COMMAND -- $CONF

end script
--------------------------------------------------------------------

$ sudo service redis-uve start

/etc/init/redis-query.conf
--------------------------------------------------------------------
# redis-server query
#

description     "redis-server query"

start on runlevel [2345]
stop on runlevel [!2345]

chdir /var/run
respawn

script
  COMMAND="/usr/bin/redis-server"
  CONF="/etc/contrail/redis-query"

  # Allow override of command/conf and opts by /etc/default/daemon-name
  if [ -f /etc/default/$UPSTART_JOB ]; then
    . /etc/default/$UPSTART_JOB
  fi

  if ! [ -r "$CONF" ] ; then
    echo "Could not read ${CONF}: exiting"
    exit 0
  fi

  exec start-stop-daemon --start \
        --pidfile /var/run/${UPSTART_JOB}.pid \
        --exec $COMMAND -- $CONF

end script
--------------------------------------------------------------------

$ sudo service redis-uve start

## Collector

Update [DISCOVERY] in /etc/contrail-collector.conf.
$ sudo service contrail-collector restart

Check discovery for the registration of collector.
$ curl http://127.0.0.1:5998/services

## Query Engine

## Analytics API Server

$ curl http://127.0.0.1:8081/analytics/uves/generators
$ contrail-logs


# Control Node

## Install Packages

$ echo "deb http://ppa.launchpad.net/opencontrail/ppa/ubuntu precise main" | sudo tee -a /etc/apt/sources.list.d/opencontrail.list
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 16BD83506839FE77
$ sudo apt-get update

$ sudo apt-get install contrail-control

## Control

Update username and password in [IFMAP] in /etc/control-node.conf.
Update [DISCOVERY].

$ sudo service contrail-control restart

Check discovery for the registration of control (xmpp-server).
$ curl http://127.0.0.1:5998/services

Check analytics.
curl http://127.0.0.1:8081/analytics/uves/generators | python -mjson.tool

## DNS


# Compute Node

## Install Packages

$ echo "deb http://ppa.launchpad.net/opencontrail/ppa/ubuntu precise main" | sudo tee -a /etc/apt/sources.list.d/opencontrail.list
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 16BD83506839FE77
$ sudo apt-get update

$ sudo apt-get install contrail-vrouter-agent

$ sudo modprobe vrouter
$ echo "vrouter" | sudo tee -a /etc/modules


## vRouter Agent

Patch /etc/contrail/contrail-vrouter-agent.conf.
--------------------------------------------------------
 # IP address of discovery server
-# server=10.204.217.52
+server=10.8.1.10

 [VIRTUAL-HOST-INTERFACE]
 # Everything in this section is mandatory

 # name of virtual host interface
-# name=vhost0
+name=vhost0

 # IP address and prefix in ip/prefix_len format
-# ip=10.1.1.1/24
+ip=10.8.1.11/24

 # Gateway IP address for virtual host
-# gateway=10.1.1.254
+gateway=10.8.1.254

 # Physical interface name to which virtual host interface maps to
-# physical_interface=vnet0
+physical_interface=eth1
--------------------------------------------------------

Patch /etc/network/interfaces.
--------------------------------------------------------
auto eth1
iface eth1 inet static
        address 0.0.0.0
        up ifconfig $IFACE up
        down ifconfig $IFACE down
 
auto vhost0
iface vhost0 inet static
        pre-up vif --create vhost0 --mac $(cat /sys/class/net/eth1/address)
        pre-up vif --add vhost0 --mac $(cat /sys/class/net/eth1/address) --vrf 0 --mode x --type vhost
        pre-up vif --add eth1 --mac $(cat /sys/class/net/eth1/address) --vrf 0 --mode x --type physical
        address 10.8.1.11
        netmask 255.255.255.0
        #network 10.8.1.0
        #broadcast 10.8.1.255
        #gateway 10.8.1.254
        # dns-* options are implemented by the resolvconf package, if installed
        dns-nameservers 8.8.8.8
--------------------------------------------------------

$ sudo service networking restart
$ sudo service contrail-vrouter-agent restart

Check the configuration.
$ ip addr list

Reboot compute node!
$ sudo reboot now

Check introspec of vRouter agent.
http://10.84.53.60:8085/Snh_AgentXmppConnectionStatusReq


## Install Docker on Compute Node

$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
$ echo "deb https://get.docker.io/ubuntu docker main" | sudo tee -a /etc/apt/sources.list.d/docker.list
$ sudo apt-get update
$ sudo apt-get install lxc-docker

Download Ubuntu image and check if it works.
$ sudo docker run -i -t ubuntu /bin/bash


## Add tenant "admin"

Get utiliy.
$ git clone https://github.com/pedro-r-marques/opencontrail-netns.git

Install vRouter API.
$ sudo apt-get install python-contrail-vrouter-api


Start two Docker containers. Type Ctrl-p and Ctrl-q to leave the container.
$ sudo docker run -i -t ubuntu /bin/bash
$ sudo docker run -i -t ubuntu /bin/bash

Find out the container ID.
$ sudo docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
dccf1ec5a438        ubuntu:latest       "bash"              38 minutes ago      Up 38 minutes                           naughty_mcclintock   
0996f6040d5d        ubuntu:latest       "bash"              38 minutes ago      Up 38 minutes                           sleepy_brown

Create IPAM, policy (pass all) and virtual networks.
$ config add ipam ipam-default
$ config add policy policy-default
$ config add network front-end --ipam ipam-default --subnet 192.168.10.0/24 --policy policy-default
$ config add network back-end --ipam ipam-default --subnet 192.168.20.0/24 --policy policy-default


Run docker.py.
$ python docker.py -s 10.8.1.10 -n front-end --project admin --start dccf1ec5a438
$ python docker.py -s 10.8.1.10 -n back-end --project admin --start 0996f6040d5d

Attach into container, will see new interface veth0 and IP allocated from VN.
Ping to another container works.
$ sudo docker attach 0996f6040d5d

root@0996f6040d5d:/# ip addr list
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default 
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
36: veth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 02:55:dd:ee:5e:e3 brd ff:ff:ff:ff:ff:ff
    inet 192.168.20.253/24 brd 192.168.20.255 scope global veth0
    inet6 fe80::55:ddff:feee:5ee3/64 scope link 
       valid_lft forever preferred_lft forever


