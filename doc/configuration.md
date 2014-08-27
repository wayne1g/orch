#Command line utility to configure Contrail

##Files
```
config
config_shell.py
config_obj.py
```
##Syntax
```
config [access options] <command> <object> [name] [options]

  access options:
    Options to access API server of OpenStack and OpenContrail.
    --username <user name>
    --password <user password>
    --region <region name>
    --tenant <tenant name>
    --api-server <API server IP address>

  <command> <object> [name] [options]:

    add vdns <name>
      --domain-name <name>
      --record-order [ random | fixed | round-robin ]
      --next-dns <name>

    show vdns [name]

    delete vdns <name>

    add ipam <name>
      --dns-type [ none | default | virtual | tenant ]
      --virtual-dns <virtual DNS>
      --tenant-dns <tenant DNS>
      --domain-name <domain name>
      --ntp-server <NTP server>

    show ipam [name]

    delete ipam <name>

    add policy <name>
      --direction [ <> | > ]
      --protocol [any | tcp | udp | icmp]
      --src-net <source network>
      --dst-net <destination network>
      --src-port <start:end>
      --dst-port <start:end>
      --action [ pass | deny | drop | reject | alert | log | service ]
      --service <service>

    show policy <name>

    delete policy <name>
      --rule <rule index>

    add security-group <name>
        --rule <rule index>
        --direction [ ingress | egress ]
        --protocol [any | tcp | udp | icmp]
        --address <prefix/length>
        --port <start:end>

    show security-group [name]

    delete security-group <name>

    add network <name>
        --ipam <IPAM>
        --subnet <prefix/length>
        --gateway <gateway>
        --policy <policy>
        --route-target <route target>
        --route-table <route table>
        --l2

    show network [name]

    delete network <name>
        --policy <policy>
        --route-target <route target>
        --route-table <route table>

    add floating-ip-pool <network>:<pool>

    show floating-ip-pool [<network>:<pool>]

    delete floating-ip-pool <network>:<pool>

    add vm <name>
        --image <image>
        --flavor <flavor>
        --network <network>
        --node <node name>
        --user-data <file name>
        --wait

    show vm [name]

    delete vm <name>

    add interface-route-table <name>
        --route <prefix/length>

    show interface-route-table [name]

    delete interface-route-table <name>

    add vm-interface <VM>:<network>
        --interface-route-table <name>
        --security-group <name>
        --floating-ip-pool <tenant>:<network>:<pool>
        --floating-ip any | <IP>

    show vm-interface <VM>:<network>

    delete vm-interface <VM>:<network>
        --interface-route-table <name>
        --security-group <name>
        --floating-ip

    add route-table <name>
        --route <prefix/length:next-hop>

    show route-table [name]

    delete route-table <name>
        --route <prefix/length:next-hop>

    add service-template <name>
        --mode [ transparent | in-network | in-network-nat ]
        --type [ firewall | analyzer ]
        --image <name>
        --flavor <name>
        --scale
        --interface-type [ management | left | right | other ]

    show service-template [name]

    delete service-template <name>

    add service-instance <name>
        --template <name>
        --management-network <name>
        --left-network <name>
        --left-route <prefix/length>
        --right-network <name>
        --right-route <prefix/length>
        --scale-max <number>
        --auto-policy

    show service-instance [name]

    delete service-instance <name>

    add link-local <name>
        --link-local-address <link local address>:<link local port>
        --fabric-address '<fabric address>:<fabric port>'

    show link-local [name]

    delete link-local <name>

    show image

    show flavor
```


##Examples
### Allocate floating IP to VM interface.
```
# config add ipam ipam-default
# config add policy policy-default
# config add network front-end --ipam ipam-default --subnet 192.168.1.0/24 --policy policy-default
# config add network back-end --ipam ipam-default --subnet 192.168.1.0/24 --policy policy-default
# config add vm server --image "CentOS 6.4 1-6" --flavor m1.small --network front-end
# config add vm database --image "CentOS 6.4 1-6" --flavor m1.small --network back-end
```
### Allocate floating IP to VM interface.
```
# config add network public --ipam ipam-default --sbunet 10.8.10.0/24 --route-target 64512:10000
# config add floating-ip-pool public-pool --network public
# config add vm-interface server:front-end --floating-ip --floating-ip-pool public-pool
```
### Create layer-3 service template and service instance.
```
# config add service template vsrx-l3 --mode in-network --type firewall --image vsrx-12.1x47 --flavor m1.medium --interface-type management --interface-type left --interface-type right
# config add service-instance vsrx-l3 --template vsrx-l2 --management-network management --left-network front-end --right-network backend
# config add policy vsrx-l3 --src-net front-end --dst-net back-end --action service --service vsrx-l3
# config add network front-end --policy vsrx-l3
# config add network back-end --policy vsrx-l3
```
### Create layer-2 service template and service instance.
```
# config add service template vsrx-l2 --mode transparent --type firewall --image vsrx-12.1x47 --flavor m1.medium --interface-type management --interface-type left --interface-type right
# config add service-instance vsrx-l2 --template vsrx-l2 --management-network management
```

