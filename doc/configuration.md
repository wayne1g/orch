
Command line utility to configure Contrail.

## Create virtual networks and virtual machines.

config add ipam ipam-default

config add policy policy-default

config add network front-end --ipam ipam-default --subnet 192.168.1.0/24 --policy policy-default

config add network back-end --ipam ipam-default --subnet 192.168.1.0/24 --policy policy-default

config add vm server --image "CentOS 6.4 1-6" --flavor m1.small --network front-end

config add vm database --image "CentOS 6.4 1-6" --flavor m1.small --network back-end


## Allocate floating IP to VM interface.

config add network public --ipam ipam-default --sbunet 10.8.10.0/24 --route-target 64512:10000

config add floating-ip-pool public-pool --network public

config add vm-interface server:front-end --floating-ip --floating-ip-pool public-pool


## Create layer-3 service template and service instance.

config add service template vsrx-l3 --mode in-network --type firewall --image vsrx-12.1x47 --flavor m1.medium --interface-type management --interface-type left --interface-type right

config add service-instance vsrx-l3 --template vsrx-l2 --management-network management --left-network front-end --right-network backend

config add policy vsrx-l3 --src-net front-end --dst-net back-end --action service --service vsrx-l3

config add network front-end --policy vsrx-l3

config add network back-end --policy vsrx-l3


## Create layer-2 service template and service instance.

config add service template vsrx-l2 --mode transparent --type firewall --image vsrx-12.1x47 --flavor m1.medium --interface-type management --interface-type left --interface-type right

config add service-instance vsrx-l2 --template vsrx-l2 --management-network management


## Interface route table

config add interface-route-table irt

config add interface-route-table irt --route 10.1.1.0/24

config add vm-interface server:front-end --interface-route-table irt


